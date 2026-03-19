import queue
import sys
import json
import asyncio
import os
import subprocess
import sounddevice as sd
import vosk
import threading
import customtkinter as ctk

from command_parser import parse_command
from browser_controller import send_command_to_browser
from desktop_controller import execute_desktop_action

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

import config

class VoiceControllerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Voice Controller v2 - Next Gen")
        self.geometry("450x660")
        self.resizable(False, False)
        
        # State
        self.is_listening = False
        self.running = True
        self.model = None
        
        # Setup UI
        self.setup_ui()
        
        # Start Voice thread (Daemon thread will automatically close when window closes)
        self.voice_thread = threading.Thread(target=self.voice_loop, daemon=True)
        self.voice_thread.start()

    def setup_ui(self):
        self.label_title = ctk.CTkLabel(self, text="Voice Controller AI", font=("Segoe UI", 28, "bold"))
        self.label_title.pack(pady=(20, 5))
        
        self.label_status = ctk.CTkLabel(self, text="Status: Loading Neural Model...", text_color="orange", font=("Segoe UI", 16))
        self.label_status.pack(pady=5)
        
        self.btn_toggle = ctk.CTkButton(self, text="Start Listening", command=self.toggle_listening, state="disabled", height=50, width=200, font=("Segoe UI", 18, "bold"))
        self.btn_toggle.pack(pady=(20, 10))
        
        self.btn_browser = ctk.CTkButton(self, text="Launch Compatible Browser", command=self.launch_browser, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_browser.pack(pady=10)
        
        self.log_textbox = ctk.CTkTextbox(self, width=400, height=120, font=("Consolas", 12))
        self.log_textbox.pack(pady=(15, 10))
        self.log_textbox.insert("0.0", "--- Application Logs ---\n")
        self.log_textbox.configure(state="disabled")
        
        # --- Speed Settings Frame ---
        self.settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_frame.pack(pady=5, fill="x", padx=25)
        
        self.lbl_fast = ctk.CTkLabel(self.settings_frame, text="Fast (x):", font=("Segoe UI", 12))
        self.lbl_fast.pack(side="left", padx=(0, 5))
        
        self.entry_fast = ctk.CTkEntry(self.settings_frame, width=50, height=28)
        self.entry_fast.insert(0, str(config.SPEED_FAST))
        self.entry_fast.pack(side="left", padx=5)
        
        self.lbl_vfast = ctk.CTkLabel(self.settings_frame, text="Super Fast (x):", font=("Segoe UI", 12))
        self.lbl_vfast.pack(side="left", padx=(15, 5))
        
        self.entry_vfast = ctk.CTkEntry(self.settings_frame, width=50, height=28)
        self.entry_vfast.insert(0, str(config.SPEED_VERY_FAST))
        self.entry_vfast.pack(side="left", padx=5)
        
        self.btn_save_config = ctk.CTkButton(self.settings_frame, text="Save", width=60, height=28, command=self.save_settings)
        self.btn_save_config.pack(side="right", padx=5)
        
        # --- Voice Commands Help ---
        help_text = (
            "Available Voice Commands:\n"
            "▶️ 'go', 'play'  |  ⏸️ 'stop', 'pause'\n"
            "⏩ 'frank' (+10s), 'leap' (+20s), 'post' (+30s)\n"
            "⏪ 'back' (-10s), 'rep' (-20s), 'please read' (-30s)\n"
            "🚀 'fast', 'super fast', 'normal speed'"
        )
        self.help_frame = ctk.CTkFrame(self)
        self.help_frame.pack(pady=15, fill="x", padx=25)
        
        self.lbl_help = ctk.CTkLabel(self.help_frame, text=help_text, justify="center", font=("Segoe UI", 13, "bold"), text_color="#A9B1D6")
        self.lbl_help.pack(pady=10)
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def save_settings(self):
        try:
            fast = self.entry_fast.get()
            super_fast = self.entry_vfast.get()
            config.save_config(fast, super_fast)
            self.log(f"Saved Settings - Fast: {fast}x, Super: {super_fast}x")
        except Exception as e:
            self.log("Invalid speed number entered!")

    def log(self, text):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def toggle_listening(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.btn_toggle.configure(text="Pause Listening", fg_color="#C62828", hover_color="#8E0000") # Red
            self.label_status.configure(text="Status: Listening 🎙️", text_color="#00E676") # Green
            self.log("Microphone Active.")
        else:
            self.btn_toggle.configure(text="Start Listening", fg_color="#1f538d", hover_color="#14375e") # Blue
            self.label_status.configure(text="Status: Paused ⏸️", text_color="orange")
            self.log("Microphone Paused.")

    def launch_browser(self):
        import winreg
        import shlex
        self.log("Identifying default browser...")
        
        browser_path = ""
        try:
            # 1. Figure out what the default browser ProgID is
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                prog_id = winreg.QueryValueEx(key, "ProgId")[0]
            
            # 2. Look up the exact command used to launch that ProgID
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\shell\open\command") as key:
                command = winreg.QueryValueEx(key, "")[0]
                
            # Parse out the actual exe path (handles quotes correctly)
            parts = shlex.split(command)
            browser_path = parts[0]
            
            self.log(f"Found Default Browser: {os.path.basename(browser_path)}")
            
        except Exception as e:
            self.log(f"Could not dictate default browser perfectly: {e}")
            self.log("Falling back to standard Chrome...")
            # Fallback path if registry reads fail
            browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        # Now launch whatever browser we found with the specific debugging ports we need
        self.log(f"Launching with Debug Port 9222...")
        
        # We must put quotes around the browser path if it has spaces
        safe_browser_path = f'"{browser_path}"' if " " in browser_path else browser_path
        
        # Kill conflicting instances so the debug port definitely works 
        subprocess.run('taskkill /F /IM chrome.exe /T 2>nul', shell=True)
        subprocess.run('taskkill /F /IM thorium.exe /T 2>nul', shell=True)
        subprocess.run('taskkill /F /IM brave.exe /T 2>nul', shell=True)
        subprocess.run('taskkill /F /IM msedge.exe /T 2>nul', shell=True)
        
        cmd = rf'start "" {safe_browser_path} --remote-debugging-port=9222 "https://www.youtube.com"'
        
        try:
            subprocess.Popen(cmd, shell=True)
            self.log("Browser window opened successfully.")
        except Exception as e:
            self.log(f"Failed to launch browser: {e}")

    def voice_loop(self):
        # Helper to find paths whether running as Python script or packaged Exe
        def resource_path(relative_path):
            try:
                base_path = sys._MEIPASS
            except Exception:
                base_path = os.path.dirname(os.path.abspath(__file__))
            return os.path.join(base_path, relative_path)

        # 1. Load Model
        model_path = resource_path("models/vosk-model-small-en-us-0.15")
        if not os.path.exists(model_path):
            model_path = resource_path("models/vosk-model-small-en-us")
        
        self.after(0, lambda: self.log(f"Attempting to load model from: {model_path}"))
        
        try:
            self.model = vosk.Model(model_path)
            # Safely update GUI from thread using 'after'
            self.after(0, lambda: self.btn_toggle.configure(state="normal"))
            self.after(0, lambda: self.label_status.configure(text="Status: Ready", text_color="#00B0FF")) # Cyan
            self.after(0, lambda: self.log("AI Model Loaded Successfully!"))
        except Exception as model_err:
            err_msg = str(model_err)
            self.after(0, lambda: self.label_status.configure(text="Status: Model Load Error", text_color="red"))
            self.after(0, lambda: self.log(f"Error: {err_msg}"))
            return

        samplerate = 16000
        try:
            with sd.RawInputStream(samplerate=samplerate, blocksize=1600, device=None,
                                   dtype='int16', channels=1, callback=callback):
                rec = vosk.KaldiRecognizer(self.model, samplerate)
                
                while self.running:
                    try:
                        data = q.get(timeout=0.5) 
                    except queue.Empty:
                        continue
                    
                    if not self.is_listening:
                        # Flush queue to save CPU
                        while not q.empty():
                            try:
                                q.get_nowait()
                            except queue.Empty:
                                break
                        continue
                        
                    action_found = False
                    
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        text = result.get("text", "")
                        if text:
                            self.after(0, lambda t=text: self.log(f"🎙️ AI Evaluated: '{t}'"))
                            action = parse_command(text)
                            if action:
                                action_found = True
                    else:
                        partial = json.loads(rec.PartialResult())
                        partial_text = partial.get("partial", "")
                        if partial_text:
                            action = parse_command(partial_text)
                            if action:
                                action_found = True
                                self.after(0, lambda p=partial_text: self.log(f"Heard: '{p}'"))
                                
                    if action_found:
                        self.after(0, lambda a=action: self.log(f"Executing: {a}"))
                        success = asyncio.run(send_command_to_browser(action))
                        if success:
                            self.after(0, lambda: self.log("✅ Executed in Browser"))
                        else:
                            self.after(0, lambda: self.log("⚠️ Fallback to Desktop Keys"))
                            execute_desktop_action(action)
                        
                        rec.Reset()
        except Exception as mic_err:
            err_msg_mic = str(mic_err)
            self.after(0, lambda: self.log(f"Microphone Error: {err_msg_mic}"))
            
    def on_closing(self):
        self.running = False
        self.destroy()

if __name__ == "__main__":
    app = VoiceControllerGUI()
    app.mainloop()
