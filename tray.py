import pystray
from PIL import Image
import threading
import os

class AppTray:
    def __init__(self, start_callback, stop_callback, quit_callback):
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.quit_callback = quit_callback
        self.icon = None
        self.is_listening = True

    def get_image(self):
        """Loads the icon image from the assets folder."""
        icon_path = "assets/icon.png"
        if os.path.exists(icon_path):
            return Image.open(icon_path)
        else:
            # Fallback icon if the image doesn't exist
            return Image.new('RGB', (64, 64), color='gray')

    def on_toggle(self, icon, item):
        """Toggles the listening state and updates the tray icon text."""
        self.is_listening = not self.is_listening
        
        # We can update the hover text of the icon
        self.icon.title = f"Voice Controller [{'Active' if self.is_listening else 'Paused'}]"
        
        if self.is_listening:
            self.start_callback()
        else:
            self.stop_callback()

    def on_quit(self, icon, item):
        """Quits the application entirely."""
        self.icon.stop()
        self.quit_callback()

    def run_detached(self):
        """
        Runs the system tray icon loop in a separate thread.
        This prevents the tray icon from blocking our main voice recognition loop.
        """
        image = self.get_image()
        
        menu = pystray.Menu(
            pystray.MenuItem(
                # Dynamic text based on current state
                lambda text: 'Pause Listening' if self.is_listening else 'Resume Listening', 
                self.on_toggle
            ),
            pystray.MenuItem('Quit Voice Controller', self.on_quit)
        )
        
        self.icon = pystray.Icon("VoiceController", image, "Voice Controller [Active]", menu)
        
        # Start pystray loop in a daemon thread so it dies when main process dies
        tray_thread = threading.Thread(target=self.icon.run)
        tray_thread.daemon = True 
        tray_thread.start()

if __name__ == "__main__":
    import time
    import sys

    # Mock callbacks for testing
    def mock_start():
        print("Listening started...")

    def mock_stop():
        print("Listening paused...")

    def mock_quit():
        print("Quitting app...")
        sys.exit(0)

    print("Starting tray application.")
    print("Check your system tray (bottom right corner, near the clock) for the icon.")
    print("Right-click it to see the menu.")
    
    tray = AppTray(mock_start, mock_stop, mock_quit)
    tray.run_detached()
    
    # Keep main thread alive for testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTest interrupted")
