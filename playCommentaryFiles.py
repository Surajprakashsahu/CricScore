import os
import glob
import time
import simpleaudio as sa
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

IMAGE_FOLDER = config['DEFAULT']['AUDIO_FOLDER']

folder = "/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Resposes/audio-files"
played_files = set()

def get_sorted_wavs():
    wav_files = glob.glob(os.path.join(folder, "*.wav"))
    wav_files.sort(key=lambda x: os.path.getctime(x))
    return wav_files

print("Monitoring for new .wav files. Press Ctrl+C to exit.")

try:
    while True:
        wav_files = get_sorted_wavs()
        for wav in wav_files:
            if wav not in played_files:
                print(f"Playing: {os.path.basename(wav)}")
                wave_obj = sa.WaveObject.from_wave_file(wav)
                play_obj = wave_obj.play()
                play_obj.wait_done()
                played_files.add(wav)
        time.sleep(2)  # Check for new files every 2 seconds
except KeyboardInterrupt:
    print("Stopped monitoring.")