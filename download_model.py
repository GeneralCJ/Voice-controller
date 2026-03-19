import os
import urllib.request
import zipfile

url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
zip_path = "models/vosk-model-small-en-us.zip"
extract_path = "models/"

print(f"Downloading Vosk model from {url}...")
os.makedirs("models", exist_ok=True)
urllib.request.urlretrieve(url, zip_path)

print("Extracting Vosk model...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

print("Cleaning up...")
os.remove(zip_path)

print("Vosk model downloaded and extracted successfully!")
