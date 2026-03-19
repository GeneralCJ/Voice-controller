import json
import os

# config.py
# Customizable settings for the Voice Controller application

# The number of seconds to jump forward or backward when a seek command is recognized.
SKIP_SECONDS = 10

# Playback speed multipliers (Defaults)
SPEED_FAST = 1.5
SPEED_VERY_FAST = 2.0
SPEED_NORMAL = 1.0

# Path to the settings JSON file
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

def load_config():
    global SPEED_FAST, SPEED_VERY_FAST
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                SPEED_FAST = data.get("SPEED_FAST", SPEED_FAST)
                SPEED_VERY_FAST = data.get("SPEED_VERY_FAST", SPEED_VERY_FAST)
        except Exception:
            pass # Use defaults if corrupted
            
def save_config(fast_val, very_fast_val):
    global SPEED_FAST, SPEED_VERY_FAST
    SPEED_FAST = float(fast_val)
    SPEED_VERY_FAST = float(very_fast_val)
    
    data = {
        "SPEED_FAST": SPEED_FAST,
        "SPEED_VERY_FAST": SPEED_VERY_FAST
    }
    
    try:
        with open(SETTINGS_PATH, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Failed to save settings: {e}")

# Automatically load settings if they exist when config is imported
load_config()
