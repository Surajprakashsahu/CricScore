#!/usr/bin/env python3
"""
Test text cleaning for TTS
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generateCommentry import clean_description_for_tts

def test_text_cleaning():
    # Test with the problematic text
    test_text = """Okay, here are a few options for an audio-friendly description, keeping it under 2-3 sentences and aiming for excitement:

Option 1 (Energetic):

"Hold on! The pressure's on as [Team Name] fight back! Can they snatch this wicket? It's nail-biting cricket!"

Option 2 (Slightly More Detailed):

"We're live and it's a tense moment! [Player Name] has just bowled a stunning delivery and [Team Name] are under pressure. It's a crucial over – will they hold on?"

---

To help me tailor the description even better, could you tell me:"""

    cleaned = clean_description_for_tts(test_text)
    print('✅ Text cleaning test:')
    print(f'Original length: {len(test_text)}')
    print(f'Cleaned length: {len(cleaned)}')
    print(f'Cleaned text: {cleaned}')
    
    # Test with short text
    short_text = "Hi"
    cleaned_short = clean_description_for_tts(short_text)
    print(f'\n✅ Short text test: "{short_text}" -> "{cleaned_short}"')

if __name__ == "__main__":
    test_text_cleaning()
