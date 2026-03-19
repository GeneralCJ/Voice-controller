# Voice-controller
A lightweight, 100% offline Windows desktop application that controls browser video playback (play, pause, seek, speed) using zero-latency voice commands. Built to enable completely hands-free video control without relying on cloud APIs or browser extensions.
# 🎙️ AI Voice Controller

A lightweight, 100% offline Windows desktop app that lets you control video playback in any Chromium browser using voice commands. Build for taking hand-written notes without touching the keyboard. 

## 🚀 Features
- **Zero-Latency Offline Recognition:** Powered by the Vosk speech-to-text model (~50MB).
- **Native Browser Control:** Connects via Chrome DevTools Protocol (CDP), bypassing buggy browser extensions.
- **Hands-Free Media:** Play, pause, seek (±10s, 20s, 30s), and adjust speed using voice triggers.
- **Phonetic Matching:** Optimized phrase detection for near 100% accuracy on minimal hardware.
- **GUI & Live Logs:** Easy-to-use CustomTkinter interface with settings management.

## 🛠️ Tech Stack
- **Python 3**
- **Vosk** (Speech Recognition)
- **WebSockets / CDP** (Browser DOM Control)
- **Sounddevice** (Mic Input)
- **CustomTkinter** (User Interface)

## ⚙️ How to Use
1. Clone the repo and run `pip install -r requirements.txt`
2. Extract `vosk-model-small-en-us` into the `models/` folder.
3. Launch your browser (Chrome/Brave) with: `--remote-debugging-port=9222`
4. Run `python main.py` and start speaking!
