import torch
from TTS.api import TTS
import json
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

# Determine if a GPU is available and set the device
device = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False).to(device)

input_folder = config['DEFAULT']['RESPONSE_FOLDER']
output_folder = config['DEFAULT']['AUDIO_FOLDER']

def read_description_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        description = json_data.get("description")
        if not description:
            print(f"Error: 'description' field not found in {file_path}.")
        return description
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def generate_audio_from_json(input_json_file, output_audio_file):
    text_data = read_description_from_json(input_json_file)
    if text_data:
        print(f"Generating audio from description in {input_json_file}...")
        try:
            tts.tts_to_file(text=text_data, file_path=output_audio_file)
            print(f"Audio file successfully saved to {output_audio_file}")
        except Exception as e:
            print(f"An error occurred during audio generation: {e}")

def process_all_json_files():
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_json_file = os.path.join(input_folder, filename)
            output_audio_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.wav")
            if not os.path.exists(output_audio_file):
                generate_audio_from_json(input_json_file, output_audio_file)

class NewJsonHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".json"):
            filename = os.path.basename(event.src_path)
            output_audio_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.wav")
            generate_audio_from_json(event.src_path, output_audio_file)

if __name__ == "__main__":
    print("Processing existing JSON files...")
    process_all_json_files()
    print("Watching for new JSON files...")
    event_handler = NewJsonHandler()
    observer = Observer()
    observer.schedule(event_handler, input_folder, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()