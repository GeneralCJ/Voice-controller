import time
from browser_controller import execute_browser_action
from command_parser import ACTION_PAUSE, ACTION_PLAY, ACTION_FORWARD_10, ACTION_BACKWARD_10

print("Starting automated Browser Controller test...")
print("Make sure the YouTube video is visible on your screen.")

print("\n1. Testing PLAY in 5 seconds...")
time.sleep(5)
execute_browser_action(ACTION_PLAY)

print("\n2. Testing PAUSE in 5 seconds...")
time.sleep(5)
execute_browser_action(ACTION_PAUSE)

print("\n3. Testing FORWARD 10s in 5 seconds...")
time.sleep(5)
execute_browser_action(ACTION_FORWARD_10)

print("\n4. Testing BACKWARD 10s in 5 seconds...")
time.sleep(5)
execute_browser_action(ACTION_BACKWARD_10)

print("\nTest complete! Did it work?")
