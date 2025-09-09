import ollama
import os
import time
import json
import re
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.properties')

# IMAGE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Images'
# RESPONSE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Resposes'
# MODEL_NAME = 'gemma3:4b'
# PROMPT = 'Give me score and brief commentry of the over and last bowl from this image in json format with keys score and description.'
IMAGE_FOLDER = config['DEFAULT']['IMAGE_FOLDER']
RESPONSE_FOLDER = config['DEFAULT']['RESPONSE_FOLDER']
MODEL_NAME = config['DEFAULT']['MODEL_NAME']
PROMPT = config['DEFAULT']['PROMPT']

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def process_image(image_path):
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting to process image: {os.path.basename(image_path)}")
    start_time = time.time()
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                'role': 'user',
                'content': PROMPT,
                'images': [image_path]
            }
        ]
    )
    
    processing_time = time.time() - start_time
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Image processing completed in {processing_time:.2f} seconds")
    
    return response['message']['content']

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def safe_remove_file(file_path):
    """Safely remove a file and handle any potential errors."""
    try:
        os.remove(file_path)
        print(f"Successfully removed {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error removing file {file_path}: {e}")

def process_new_images():
    """Process any new images in the folder."""
    current_files = set(os.path.join(IMAGE_FOLDER, f) for f in os.listdir(IMAGE_FOLDER))
    new_files = current_files - processed
    
    if new_files:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detected {len(new_files)} new image(s)")
    
    for fpath in new_files:
        if os.path.basename(fpath).lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New image detected: {os.path.basename(fpath)}")
                
                result = process_image(fpath)
                print(f"Raw response for {os.path.basename(fpath)}: {result}")
                
                # Extract and parse the JSON part
                json_str = extract_json(result)
                if not json_str:
                    print(f"No JSON found in response from {os.path.basename(fpath)}")
                    continue
                
                try:
                    result_json = json.loads(json_str)
                except Exception as e:
                    print(f"Error parsing JSON from {os.path.basename(fpath)}: {e}")
                    continue
                
                resp_path = os.path.join(RESPONSE_FOLDER, f"{os.path.splitext(os.path.basename(fpath))[0]}.json")
                with open(resp_path, 'w') as f:
                    json.dump(result_json, f, indent=2)
                
                processed.add(fpath)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully processed and saved JSON for: {os.path.basename(fpath)}")
                
                # Remove the processed image file
                safe_remove_file(fpath)
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing {os.path.basename(fpath)}: {e}")
    
    return bool(new_files)

def main():
    global processed
    processed = set()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting image processing service...")
    print(f"Monitoring folder: {IMAGE_FOLDER}")
    print(f"Using model: {MODEL_NAME}")
    
    last_check = 0
    check_interval = 60  # Regular check interval in seconds
    quick_check_interval = 1  # Quick check interval in seconds
    
    while True:
        current_time = time.time()
        
        if current_time - last_check >= check_interval:
            # Do a regular check and update the last check time
            found_new = process_new_images()
            last_check = current_time
            
            if not found_new:
                # If no new images, wait for the regular interval
                time.sleep(check_interval)
        else:
            # Do a quick check for new images
            if process_new_images():
                # If we found and processed new images, continue quick checking
                time.sleep(quick_check_interval)
            else:
                # If no new images in quick check, wait for the remainder of the regular interval
                time.sleep(check_interval - (time.time() - last_check))

if __name__ == "__main__":
    main()