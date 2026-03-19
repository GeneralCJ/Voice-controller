import re

# Action constants
ACTION_PAUSE = "PAUSE"
ACTION_PLAY = "PLAY"
ACTION_FORWARD_10 = "FORWARD_10"
ACTION_FORWARD_20 = "FORWARD_20"
ACTION_FORWARD_30 = "FORWARD_30"

ACTION_BACKWARD_10 = "BACKWARD_10"
ACTION_BACKWARD_20 = "BACKWARD_20"
ACTION_BACKWARD_30 = "BACKWARD_30"

ACTION_SPEED_FAST = "SPEED_FAST"
ACTION_SPEED_VERY_FAST = "SPEED_VERY_FAST"
ACTION_SPEED_NORMAL = "SPEED_NORMAL"

# Command mapping based on user specifications
COMMANDS = {
    ACTION_PAUSE: ["stop", "pause", "wait"],
    ACTION_PLAY: ["resume", "play", "start", "go"],
    ACTION_FORWARD_10: ["front", "frank", "friend", "forward ten", "forward 10", "skip ten", "skip 10", "next ten", "go forward", "forward", "skip"],
    ACTION_FORWARD_20: ["leap", "jump"],
    ACTION_FORWARD_30: ["boost", "dash", "post", "both"],
    ACTION_BACKWARD_10: ["back", "backward ten", "backward 10", "back ten", "back 10", "rewind ten", "rewind 10", "go backward", "backward", "go back", "rewind"],
    ACTION_BACKWARD_20: ["drop", "rep"],
    ACTION_BACKWARD_30: ["retreat", "i don't read", "please read"],
    ACTION_SPEED_FAST: ["fast", "play fast", "speed up"],
    ACTION_SPEED_VERY_FAST: ["very fast", "super fast", "play very fast", "two x", "double speed"],
    ACTION_SPEED_NORMAL: ["normal speed", "play normal", "slow down", "normal"]
}

def parse_command(text: str) -> str:
    """
    Parses the spoken text and returns a corresponding ACTION constant,
    or None if no command matched.
    """
    # Clean the text
    clean_text = text.lower().strip()
    
    if not clean_text:
        return None

    # Find the longest matching trigger phrase
    longest_match_action = None
    longest_match_len = 0
    
    for action, triggers in COMMANDS.items():
        for trigger in triggers:
            # We use word boundary matching
            if re.search(r'\b' + re.escape(trigger) + r'\b', clean_text):
                if len(trigger) > longest_match_len:
                    longest_match_len = len(trigger)
                    longest_match_action = action
                    
    return longest_match_action

if __name__ == "__main__":
    print("Testing Command Parser...")
    
    test_cases = [
        ("please pause the video", ACTION_PAUSE),
        ("stop", ACTION_PAUSE),
        ("resume", ACTION_PLAY),
        ("play the video", ACTION_PLAY),
        ("go forward 10 seconds", ACTION_FORWARD_10),
        ("forward ten please", ACTION_FORWARD_10),
        ("backward 10", ACTION_BACKWARD_10),
        ("back ten seconds", ACTION_BACKWARD_10),
        ("hello world", None),
        ("what is the weather", None)
    ]
    
    passed = 0
    for input_text, expected in test_cases:
        result = parse_command(input_text)
        status = "✅ PASS" if result == expected else f"❌ FAIL (Expected {expected}, Got {result})"
        print(f"{status} | Input: '{input_text}' -> Parsed: {result}")
        if result == expected:
            passed += 1
            
    print(f"\nResult: {passed}/{len(test_cases)} passed.")
