import os
import glob
import time
import simpleaudio as sa
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

# Use the correct config setting for audio folder
AUDIO_FOLDER = config['DEFAULT']['AUDIO_FOLDER']

played_files = set()

def get_sorted_wavs():
    wav_files = glob.glob(os.path.join(AUDIO_FOLDER, "*.wav"))
    wav_files.sort(key=lambda x: os.path.getctime(x))
    return wav_files

print("Monitoring for new .wav files. Press Ctrl+C to exit.")
print(f"Monitoring folder: {AUDIO_FOLDER}")

try:
    while True:
        wav_files = get_sorted_wavs()
        for wav in wav_files:
            if wav not in played_files:
                print(f"Playing: {os.path.basename(wav)}")
                try:
                    wave_obj = sa.WaveObject.from_wave_file(wav)
                    play_obj = wave_obj.play()
                    play_obj.wait_done()
                    played_files.add(wav)
                    print(f"Finished playing: {os.path.basename(wav)}")
                except Exception as e:
                    print(f"Error playing {os.path.basename(wav)}: {e}")
                    played_files.add(wav)  # Mark as played to avoid retry loop
        time.sleep(2)  # Check for new files every 2 seconds
except KeyboardInterrupt:
    print("Stopped monitoring.")