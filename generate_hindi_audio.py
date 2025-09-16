import json
import os
from gtts import gTTS

def main():
    in_path = "resource/cmtry/last_6_balls_commentary_hi.json"
    out_path = "resource/cmtry-audio/last_6_balls_commentary_hi_1.mp3"
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
    print(f"Generating audio for: {first_hi}")
    tts = gTTS(text=first_hi, lang='hi')
    tts.save(out_path)
    print(f"Audio saved to {out_path}")

if __name__ == "__main__":
    main()
