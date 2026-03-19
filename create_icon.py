from PIL import Image, ImageDraw
import os

def create_icon(path="assets/icon.png"):
    width = 64
    height = 64
    # Create a simple icon with a transparent background
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    
    # Dark grey outer circle
    dc.ellipse([0, 0, width, height], fill=(60, 60, 60, 255))
    
    # Microphone-like shape in the center (light grey)
    # The head of the mic
    dc.rounded_rectangle([width//2 - 10, height//4, width//2 + 10, height//2 + 12], radius=10, fill=(200, 200, 200, 255))
    
    # The stand of the mic
    dc.rectangle([width//2 - 3, height//2 + 12, width//2 + 3, height//2 + 25], fill=(200, 200, 200, 255))
    
    # The base of the mic stand
    dc.rectangle([width//2 - 15, height//2 + 25, width//2 + 15, height//2 + 28], fill=(200, 200, 200, 255))
    
    image.save(path)
    print(f"Icon saved to {path}")

if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    create_icon()
