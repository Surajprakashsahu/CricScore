import ollama
import os
import time
import json
import re

IMAGE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Images'
RESPONSE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Resposes'
MODEL_NAME = 'gemma3:4b'
PROMPT = 'Give me score and brief description of the match from this image in json format with keys score and description.'

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def process_image(image_path):
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
    return response['message']['content']

def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None

def main():
    processed = set()
    while True:
        for fname in os.listdir(IMAGE_FOLDER):
            fpath = os.path.join(IMAGE_FOLDER, fname)
            if fname.lower().endswith(('.jpg', '.jpeg', '.png')) and fpath not in processed:
                try:
                    result = process_image(fpath)
                    print(f"Raw response for {fname}: {result}")
                    # Extract and parse the JSON part
                    json_str = extract_json(result)
                    if not json_str:
                        print(f"No JSON found in response from {fname}")
                        continue
                    try:
                        result_json = json.loads(json_str)
                    except Exception as e:
                        print(f"Error parsing JSON from {fname}: {e}")
                        continue
                    resp_path = os.path.join(RESPONSE_FOLDER, f"{os.path.splitext(fname)[0]}.json")
                    with open(resp_path, 'w') as f:
                        json.dump(result_json, f, indent=2)
                    processed.add(fpath)
                    print(f"Processed {fname}")
                except Exception as e:
                    print(f"Error processing {fname}: {e}")
        time.sleep(60)

if __name__ == "__main__":
    main()