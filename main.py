import queue
import sys
import json
import asyncio
import os
import sounddevice as sd
import vosk

from command_parser import parse_command
from browser_controller import send_command_to_browser
from desktop_controller import execute_desktop_action
from tray import AppTray

q = queue.Queue()

def callback(indata, frames, time, status):
    """Called for each audio block from the microphone."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def main():
    model_path = "models/vosk-model-small-en-us-0.15"
    if not os.path.exists(model_path):
        # Fallback check just in case the folder name differs
        model_path = "models/vosk-model-small-en-us"
        if not os.path.exists(model_path):
            print(f"Model path not found. Please run download_model.py first.")
            return

    print("Loading Voice Recognition Model... (This takes a few seconds but runs completely offline)")
    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return
        
    # Shared state between tray and main loop
    app_state = {
        'running': True,
        'listening': True
    }
    
    def on_start():
        app_state['listening'] = True
        print("\n🔊 [Tray] Listening resumed. Waiting for offline voice commands...")
        
    def on_stop():
        app_state['listening'] = False
        print("\n🔇 [Tray] Listening paused. Microphone input is ignored.")
        
    def on_quit():
        app_state['running'] = False
        print("\n🚪 [Tray] Quitting application...")
        
    print("Initializing Tray Icon...")
    tray = AppTray(on_start, on_stop, on_quit)
    tray.run_detached()
    
    print("\n" + "="*50)
    print("🎙️ VOICE CONTROLLER IS ACTIVE 🎙️")
    print("="*50)
    print("Say a voice command: 'stop', 'resume', 'forward 10', 'backward 10'.")
    print("A system tray icon is available in the bottom right corner to pause or exit.")
    print("="*50 + "\n")

    samplerate = 16000
    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=1600, device=None,
                               dtype='int16', channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            
            while app_state['running']:
                try:
                    # Time out so we periodically check if app_state['running'] is false (to quit gracefully)
                    data = q.get(timeout=0.5) 
                except queue.Empty:
                    continue
                
                # If paused from tray, don't pass data to the vosk recognizer to save CPU
                if not app_state['listening']:
                    # Keep consuming the queue so it doesn't build up
                    while not q.empty():
                        try:
                            q.get_nowait()
                        except queue.Empty:
                            break
                    continue
                    
                # Variable to track if we found a command in this iteration
                action_found = False
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "")
                    if text:
                        # print(f"Voice Detected: '{text}'")
                        action = parse_command(text)
                        if action:
                            action_found = True
                            print(f"🚀 Matches Command: [{action}]")
                else:
                    # To reduce latency to zero, we check the partial result as it's streaming!
                    partial = json.loads(rec.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        action = parse_command(partial_text)
                        if action:
                            action_found = True
                            print(f"⚡ Fast Match (Instant Execution): [{action}] (from: '{partial_text}')")
                
                # If either the final or partial result matched a command:
                if action_found:
                    # 1. Try browser controller first (silent, doesn't interfere with typing)
                    success = asyncio.run(send_command_to_browser(action))
                    
                    if success:
                        print("✅ Command successfully dispatched to Browser.")
                    else:
                        # 2. Fallback to desktop controller directly simulating keys if browser CDP fails
                        print("⚠️ Browser not actively listening on CDP port. Falling back to desktop keyboard simulation...")
                        execute_desktop_action(action)
                    
                    # Reset the recognizer so it doesn't double-fire the same command!
                    rec.Reset()
    except KeyboardInterrupt:
        print("\nUser triggered KeyboardInterrupt (Ctrl+C). Exiting.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Application sequence gracefully shut down.")
        # Ensure we kill process completely 
        os._exit(0)

if __name__ == "__main__":
    main()
