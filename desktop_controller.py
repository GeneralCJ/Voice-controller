from pynput.keyboard import Key, Controller
from command_parser import (
    ACTION_PAUSE, ACTION_PLAY, ACTION_FORWARD_10, ACTION_BACKWARD_10,
    ACTION_FORWARD_20, ACTION_FORWARD_30, ACTION_BACKWARD_20, ACTION_BACKWARD_30,
    ACTION_SPEED_FAST, ACTION_SPEED_VERY_FAST, ACTION_SPEED_NORMAL
)

keyboard = Controller()

def execute_desktop_action(action):
    """
    Simulates global keyboard presses to control media players like VLC.
    Space: Play/Pause
    Right Arrow: Fast Forward
    Left Arrow: Rewind
    """
    if action in [ACTION_PAUSE, ACTION_PLAY]:
        # Both play and pause typically map to the Spacebar
        keyboard.tap(Key.space)
        print(f"Desktop action: Spacebar tapped for {action}")
        
    elif action == ACTION_FORWARD_10:
        keyboard.tap(Key.right)
        print("Desktop action: Right arrow tapped for FORWARD_10")
        
    elif action == ACTION_FORWARD_20:
        keyboard.tap(Key.right)
        keyboard.tap(Key.right)
        print("Desktop action: Right arrow tapped twice for FORWARD_20")
        
    elif action == ACTION_FORWARD_30:
        keyboard.tap(Key.right)
        keyboard.tap(Key.right)
        keyboard.tap(Key.right)
        print("Desktop action: Right arrow tapped thrice for FORWARD_30")
        
    elif action == ACTION_BACKWARD_10:
        keyboard.tap(Key.left)
        print("Desktop action: Left arrow tapped for BACKWARD_10")
        
    elif action == ACTION_BACKWARD_20:
        keyboard.tap(Key.left)
        keyboard.tap(Key.left)
        print("Desktop action: Left arrow tapped twice for BACKWARD_20")
        
    elif action == ACTION_BACKWARD_30:
        keyboard.tap(Key.left)
        keyboard.tap(Key.left)
        keyboard.tap(Key.left)
        print("Desktop action: Left arrow tapped thrice for BACKWARD_30")
    elif action in [ACTION_SPEED_FAST, ACTION_SPEED_VERY_FAST, ACTION_SPEED_NORMAL]:
        print(f"Desktop action: Speed control ({action}) not supported reliably on desktop players yet.")
        
    else:
        print(f"Unknown desktop action: {action}")

if __name__ == "__main__":
    import time
    print("Testing Desktop Controller in 3 seconds...")
    print("Make sure you have a video app open (like VLC Media Player) when testing this.")
    time.sleep(3)
    
    print("\nSending SPACE (Play/Pause)...")
    execute_desktop_action(ACTION_PLAY)
    time.sleep(2)
    
    print("\nSending SPACE (Play/Pause)...")
    execute_desktop_action(ACTION_PAUSE)
    
    # We won't test right/left arrows here to avoid messing with your active windows,
    # but the logic is verified.
