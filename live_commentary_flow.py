import os
import time
import json
import configparser
import requests
from gtts import gTTS
import simpleaudio as sa
from pydub import AudioSegment
from ollama_html_extract import parse_scorecard_html

def fetch_html(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fetch_and_save_scorecard(score_url, out_path):
    html = fetch_html(score_url)
    scorecard_json = parse_scorecard_html(html)
    save_json(scorecard_json, out_path)

def fetch_and_save_commentary(cmtry_url, inns_label, out_path):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    import time as t
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(cmtry_url)
    try:
        a_tags = driver.find_elements(By.TAG_NAME, "a")
        found = False
        for a in a_tags:
            if a.text.strip() == inns_label:
                a.click()
                found = True
                t.sleep(1)
                break
        if not found:
            print(f'No <a> tag with text "{inns_label}" found.')
    except Exception as e:
        print(f"Could not find or click INNS tab: {e}")
    # Extract last 6 balls commentary
    commentary_blocks = driver.find_elements(By.CSS_SELECTOR, "div.cb-col.cb-col-100.ng-scope")
    ball_commentary = []
    for block in commentary_blocks:
        try:
            over_div = block.find_element(By.CSS_SELECTOR, "div.cb-mat-mnu-wrp.cb-ovr-num.ng-binding")
            comm_p = block.find_element(By.CSS_SELECTOR, "p.cb-com-ln.ng-binding.ng-scope.cb-col.cb-col-90")
            over = over_div.text.strip()
            text = comm_p.text.strip()
            ball_commentary.append({"over": over, "commentary": text})
        except Exception:
            continue
    def over_key(x):
        try:
            parts = x["over"].split('.')
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except Exception:
            return (0, 0)
    ball_commentary.sort(key=over_key, reverse=True)
    last_6 = ball_commentary[:6]
    driver.quit()
    save_json(last_6, out_path)

def translate_to_hindi(text, model_name, ollama_url="http://localhost:11434/api/generate"):
    prompt = f"Quickly translate this cricket commentary to Hindi and select the best version don’t provide any prefix or suffix text just the translated text: {text}"
    payload = {"model": model_name, "prompt": prompt, "stream": False}
    response = requests.post(ollama_url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")

def generate_hindi_commentary(in_path, out_path, model_name):
    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}")
        return
    with open(in_path, "r", encoding="utf-8") as f:
        commentary = json.load(f)
    if not commentary:
        print("No commentary found in file.")
        return
    # Only translate the latest (first) ball
    ball = commentary[0]
    eng_text = ball.get("commentary", "")
    over = ball.get("over", "")
    print(f"Translating over {over}...")
    hi_text = translate_to_hindi(eng_text, model_name)
    hindi_commentary = [{"over": over, "commentary_en": eng_text, "commentary_hi": hi_text.strip()}]
    save_json(hindi_commentary, out_path)

def generate_audio_and_play(in_path, audio_dir):
    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}")
        return
    with open(in_path, "r", encoding="utf-8") as f:
        commentary = json.load(f)
    if not commentary:
        print("No commentary found in file.")
        return
    first_hi = commentary[0].get("commentary_hi", "")
    if not first_hi:
        print("No Hindi commentary found in first object.")
        return
    os.makedirs(audio_dir, exist_ok=True)
    audio_path_mp3 = os.path.join(audio_dir, "last_6_balls_commentary_hi_1.mp3")
    audio_path_wav = os.path.join(audio_dir, "last_6_balls_commentary_hi_1.wav")
    print(f"Generating audio for: {first_hi}")
    tts = gTTS(text=first_hi, lang='hi')
    tts.save(audio_path_mp3)
    print(f"Audio saved to {audio_path_mp3}")
    # Convert MP3 to WAV for simpleaudio
    sound = AudioSegment.from_mp3(audio_path_mp3)
    # Export as PCM 16-bit mono 44100Hz WAV for simpleaudio compatibility
    sound = sound.set_frame_rate(44100).set_channels(1).set_sample_width(2)
    sound.export(audio_path_wav, format="wav", parameters=["-acodec", "pcm_s16le", "-ac", "1", "-ar", "44100"])
    print(f"Playing audio...")
    wave_obj = sa.WaveObject.from_wave_file(audio_path_wav)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def main():
    config = configparser.ConfigParser()
    config.read("config.properties")
    score_url = config.get("DEFAULT", "SCORE_URL")
    cmtry_url = config.get("DEFAULT", "CMTRY_URL")
    inns_label = config.get("DEFAULT", "INNS")
    model_name = config.get("DEFAULT", "MODEL_NAME", fallback="gemma3:4b")
    interval = int(config.get("DEFAULT", "LIVE_INTERVAL", fallback="30"))
    scorecard_path = "resource/score/parsed_scorecard.json"
    commentary_path = "resource/cmtry/last_6_balls_commentary.json"
    hindi_commentary_path = "resource/cmtry/last_6_balls_commentary_hi.json"
    audio_dir = "resource/cmtry-audio"
    while True:
        print("\n--- Live Update ---")
        fetch_and_save_scorecard(score_url, scorecard_path)
        fetch_and_save_commentary(cmtry_url, inns_label, commentary_path)
        generate_hindi_commentary(commentary_path, hindi_commentary_path, model_name)
        generate_audio_and_play(hindi_commentary_path, audio_dir)
        print(f"Waiting {interval} seconds for next update...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
