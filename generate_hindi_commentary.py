import requests
import json
import configparser
import os

def translate_to_hindi(text, model_name, ollama_url="http://localhost:11434/api/generate"):
    prompt = f"Quickly translate this cricket commentary to Hindi and select the best version don’t provide any prefix or suffix text just the translated text: {text}"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(ollama_url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")

def main():
    # Load config for model name
    config = configparser.ConfigParser()
    config.read("config.properties")
    model_name = config.get("DEFAULT", "MODEL_NAME", fallback="gemma3:4b")
    in_path = "resource/cmtry/last_6_balls_commentary.json"
    out_path = "resource/cmtry/last_6_balls_commentary_hi.json"
    if not os.path.exists(in_path):
        print(f"Input file not found: {in_path}")
        return
    with open(in_path, "r", encoding="utf-8") as f:
        commentary = json.load(f)
    hindi_commentary = []
    for ball in commentary:
        eng_text = ball.get("commentary", "")
        over = ball.get("over", "")
        print(f"Translating over {over}...")
        hi_text = translate_to_hindi(eng_text, model_name)
        hindi_commentary.append({
            "over": over,
            "commentary_en": eng_text,
            "commentary_hi": hi_text.strip()
        })
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(hindi_commentary, f, indent=2, ensure_ascii=False)
    print(f"Hindi commentary saved to {out_path}")

if __name__ == "__main__":
    main()
