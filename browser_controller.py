import asyncio
import json
import urllib.request
import websockets
from command_parser import (
    ACTION_PAUSE, ACTION_PLAY, ACTION_FORWARD_10, ACTION_BACKWARD_10,
    ACTION_FORWARD_20, ACTION_FORWARD_30, ACTION_BACKWARD_20, ACTION_BACKWARD_30,
    ACTION_SPEED_FAST, ACTION_SPEED_VERY_FAST, ACTION_SPEED_NORMAL
)
import config

# Default port for Chrome remote debugging
CDP_PORT = 9222

async def get_ws_url():
    """Fetches the WebSocket URL for the first available open page in the browser."""
    try:
        # Fetch the list of targets (tabs/pages) from Chrome
        response = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json")
        targets = json.loads(response.read())
        
        # 1. First Pass: Prioritize finding an active YouTube tab
        for target in targets:
            if target.get("type") == "page" and "webSocketDebuggerUrl" in target:
                if "youtube" in target.get("url", "").lower():
                    return target["webSocketDebuggerUrl"]

        # 2. Second Pass: If no YouTube, fallback to any valid visible web page
        for target in targets:
            if target.get("type") == "page" and "webSocketDebuggerUrl" in target:
                url = target.get("url", "")
                # Ignore hidden extension/internal background pages
                if not url.startswith("chrome-extension://") and not url.startswith("chrome://"):
                    return target["webSocketDebuggerUrl"]
        
        print("No open web pages found.")
        return None
    except Exception as e:
        print(f"Failed to connect to browser on port {CDP_PORT}. Is it running with --remote-debugging-port={CDP_PORT}?")
        print(f"Error: {e}")
        return None

async def send_command_to_browser(action):
    """Sends a javascript command to the browser to execute via CDP."""
    ws_url = await get_ws_url()
    if not ws_url:
        return False

    # JavaScript snippets mapped to our actions
    js_code = {
        ACTION_PAUSE: "Array.from(document.querySelectorAll('video')).forEach(v => v.pause());",
        ACTION_PLAY: "Array.from(document.querySelectorAll('video')).forEach(v => v.play());",
        ACTION_FORWARD_10: f"Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime += {config.SKIP_SECONDS});",
        ACTION_FORWARD_20: "Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime += 20);",
        ACTION_FORWARD_30: "Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime += 30);",
        ACTION_BACKWARD_10: f"Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime -= {config.SKIP_SECONDS});",
        ACTION_BACKWARD_20: "Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime -= 20);",
        ACTION_BACKWARD_30: "Array.from(document.querySelectorAll('video')).forEach(v => v.currentTime -= 30);",
        ACTION_SPEED_FAST: f"Array.from(document.querySelectorAll('video')).forEach(v => v.playbackRate = {config.SPEED_FAST});",
        ACTION_SPEED_VERY_FAST: f"Array.from(document.querySelectorAll('video')).forEach(v => v.playbackRate = {config.SPEED_VERY_FAST});",
        ACTION_SPEED_NORMAL: f"Array.from(document.querySelectorAll('video')).forEach(v => v.playbackRate = {config.SPEED_NORMAL});",
    }.get(action)

    if not js_code:
        print(f"Unknown browser action: {action}")
        return False

    # The payload formatted for CDP
    message = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_code
        }
    }

    try:
        async with websockets.connect(ws_url) as websocket:
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            print(f"Sent: {action}")
            # print(f"Response: {response}") # For debugging
            return True
    except Exception as e:
        print(f"Error communicating with WebSocket: {e}")
        return False

# Quick async wrapper for easy testing
def execute_browser_action(action):
    asyncio.run(send_command_to_browser(action))

if __name__ == "__main__":
    print("Testing Browser Controller...")
    print(f"Please make sure Chrome/Brave/Edge is running with: --remote-debugging-port={CDP_PORT}")
    print("And that you have a video open (like YouTube).")
    input("Press Enter when ready to test PLAY...")
    execute_browser_action(ACTION_PLAY)
    
    input("Press Enter when ready to test PAUSE...")
    execute_browser_action(ACTION_PAUSE)
    
    input("Press Enter when ready to test FORWARD_10...")
    execute_browser_action(ACTION_FORWARD_10)
    
    input("Press Enter when ready to test BACKWARD_10...")
    execute_browser_action(ACTION_BACKWARD_10)
    print("Done!")
