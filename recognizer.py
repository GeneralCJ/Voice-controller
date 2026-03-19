import queue
import sys
import sounddevice as sd
import vosk
import json

# Setup the audio queue
q = queue.Queue()

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def test_microphone_and_vosk(model_path="models/vosk-model-small-en-us-0.15"):
    """Listens to microphone and prints recognized text."""
    print("Loading Vosk model...")
    try:
        model = vosk.Model(model_path)
    except Exception as e:
        print(f"Failed to load model from {model_path}. Error: {e}")
        print("Please ensure the model file is extracted in the 'models' directory.")
        return

    # Typical sampling rate for Vosk models
    samplerate = 16000
    device = None # Use default device

    print("Model loaded successfully.")
    print("--------------------------------------------------")
    print("Listening to your microphone. Speak now!")
    print("Say 'stop listening' to exit this test.")
    print("--------------------------------------------------\n")

    try:
        with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device,
                               dtype='int16', channels=1, callback=callback):
            rec = vosk.KaldiRecognizer(model, samplerate)
            
            while True:
                data = q.get()
                if rec.AcceptWaveform(data):
                    # Final recognition result
                    result_json = rec.Result()
                    result_dict = json.loads(result_json)
                    text = result_dict.get("text", "")
                    if text:
                        print(f"Recognized (Final): {text}")
                        if "stop listening" in text:
                            print("Exiting test...")
                            break
                else:
                    # Partial recognition (optional, good for real-time feedback)
                    partial_json = rec.PartialResult()
                    partial_dict = json.loads(partial_json)
                    partial_text = partial_dict.get("partial", "")
                    if partial_text:
                        print(f"  [Partial]: {partial_text}", end='\r')

    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    test_microphone_and_vosk()
