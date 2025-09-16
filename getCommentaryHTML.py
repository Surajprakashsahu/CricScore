import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import configparser
import json
import ollama
import re

config = configparser.ConfigParser()
config.read('config.properties')

RESPONSE_FOLDER = config['DEFAULT']['RESPONSE_FOLDER']
URL = config['DEFAULT']['CMTRY_URL']
MODEL_NAME = config['DEFAULT']['MODEL_NAME']

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def enhance_commentary_with_ai(raw_commentary):
    """Use Gemma3:4b to enhance and structure the commentary"""
    if not raw_commentary.strip():
        return "Live cricket match in progress with exciting action!"
    
    # Clean the raw commentary first
    cleaned_commentary = raw_commentary.replace('\n', ' ').strip()
    
    prompt = f"""
    Create a short, exciting cricket commentary for radio/audio based on this text:
    
    "{cleaned_commentary}"
    
    Rules:
    - Maximum 2 sentences
    - Make it exciting and natural for audio
    - No placeholders like [Team Name] or [Player Name]
    - Use the actual information provided
    - If no specific score mentioned, just describe the action
    
    Commentary:"""
    
    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        enhanced_text = response['message']['content'].strip()
        
        # Clean up any unwanted formatting
        import re
        enhanced_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', enhanced_text)  # Remove bold formatting
        enhanced_text = re.sub(r'\*([^*]+)\*', r'\1', enhanced_text)      # Remove italic formatting
        enhanced_text = re.sub(r'Commentary:\s*', '', enhanced_text)       # Remove "Commentary:" prefix
        enhanced_text = re.sub(r'^["\']|["\']$', '', enhanced_text)        # Remove quotes
        
        # If the response is still template-like or too long, use fallback
        if '[' in enhanced_text or 'Option' in enhanced_text or len(enhanced_text) > 200:
            # Fallback to simpler approach
            if 'proud' in cleaned_commentary.lower():
                return "The captain expresses pride in his team's performance despite the challenges they faced today."
            elif 'bowling' in cleaned_commentary.lower():
                return "Excellent bowling display from the team as they continue to apply pressure on the opposition."
            else:
                return "Exciting cricket action continues as both teams battle it out on the field."
        
        return enhanced_text
        
    except Exception as e:
        print(f"Error enhancing commentary with AI: {e}")
        # Simple fallback based on content
        if 'proud' in raw_commentary.lower():
            return "The team captain is proud of the fighting spirit shown by his players in this match."
        elif 'bowling' in raw_commentary.lower():
            return "Outstanding bowling performance puts pressure on the batting side."
        else:
            return "The cricket match continues with intense action between both teams."

def extract_commentary_data_from_html(html_content):
    """Extract cricket commentary data from HTML content using the specific pattern."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    commentary_data = {
        "score": "",
        "description": "",
        "lastOver": [],
        "recentBalls": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # Extract current score from multiple possible locations
        score_elements = soup.find_all('div', class_='cb-min-scr')
        if score_elements:
            commentary_data["score"] = score_elements[0].get_text(strip=True)
        
        # Alternative score extraction
        if not commentary_data["score"]:
            score_header = soup.find('div', class_='cb-scr-wll-chse')
            if score_header:
                commentary_data["score"] = score_header.get_text(strip=True)
        
        # Extract commentary using the specific pattern you provided
        commentary_paragraphs = soup.find_all('p', class_='cb-com-ln')
        commentary_texts = []
        
        for p in commentary_paragraphs[:5]:  # Get recent 5 commentary items
            # Extract text, preserving speaker names in bold
            text = ""
            for element in p.children:
                if element.name == 'b':
                    # This is a speaker name
                    text += f"{element.get_text(strip=True)} "
                elif hasattr(element, 'get_text'):
                    text += element.get_text(strip=True)
                else:
                    text += str(element).strip()
            
            cleaned_text = text.strip()
            if cleaned_text and len(cleaned_text) > 20:  # Filter out very short texts
                commentary_texts.append(cleaned_text)
        
        # Also look for ball-by-ball commentary in different format
        ball_commentary = soup.find_all('div', class_='cb-col-100 cb-scrd-itms')
        for item in ball_commentary[:3]:
            text = item.get_text(strip=True)
            if text and len(text) > 15:
                commentary_texts.append(text)
        
        # Extract recent balls information
        ball_elements = soup.find_all('div', class_='cb-ltst-wgt-hdr')
        recent_balls = []
        
        for ball_elem in ball_elements[:6]:  # Last 6 balls
            ball_text = ball_elem.get_text(strip=True)
            if ball_text:
                ball_info = {
                    "description": ball_text,
                    "runs": 0,
                    "type": "unknown"
                }
                
                # Enhanced pattern matching for ball types
                ball_text_upper = ball_text.upper()
                if any(word in ball_text_upper for word in ["FOUR", "4", "BOUNDARY"]):
                    ball_info["runs"] = 4
                    ball_info["type"] = "four"
                elif any(word in ball_text_upper for word in ["SIX", "6", "MAXIMUM"]):
                    ball_info["runs"] = 6
                    ball_info["type"] = "six"
                elif any(word in ball_text_upper for word in ["WIDE", "WD"]):
                    ball_info["runs"] = 1
                    ball_info["type"] = "wide"
                elif any(word in ball_text_upper for word in ["NO BALL", "NB", "NO-BALL"]):
                    ball_info["runs"] = 1
                    ball_info["type"] = "no-ball"
                elif any(word in ball_text_upper for word in ["OUT", "WICKET", "DISMISSED", "BOWLED", "LBW", "CAUGHT"]):
                    ball_info["runs"] = 0
                    ball_info["type"] = "wicket"
                else:
                    # Try to extract number of runs
                    run_match = re.search(r'\b([0-3])\s*(?:run|Run)', ball_text)
                    if run_match:
                        ball_info["runs"] = int(run_match.group(1))
                        ball_info["type"] = "runs" if ball_info["runs"] > 0 else "dot"
                    elif any(word in ball_text_upper for word in ["DOT", "NO RUN"]):
                        ball_info["type"] = "dot"
                
                recent_balls.append(ball_info)
        
        commentary_data["recentBalls"] = recent_balls
        
        # Combine and enhance commentary
        if commentary_texts:
            # Join the first 2 most recent commentaries
            raw_commentary = " ".join(commentary_texts[:2])
            
            # Use AI to enhance the commentary
            enhanced_description = enhance_commentary_with_ai(raw_commentary)
            commentary_data["description"] = enhanced_description
        else:
            # Fallback if no commentary found
            fallback_text = f"Live cricket action continues. Current score: {commentary_data['score']}"
            commentary_data["description"] = enhance_commentary_with_ai(fallback_text)
        
        # Extract over information
        over_elements = soup.find_all('div', class_='cb-scr-ovr-num')
        if over_elements:
            current_over = over_elements[0].get_text(strip=True)
            commentary_data["currentOver"] = current_over
        
        # Extract target/required runs if available
        target_elements = soup.find_all(string=re.compile(r'need|required|target', re.I))
        for element in target_elements:
            if element.parent:
                target_text = element.parent.get_text(strip=True)
                if len(target_text) < 100:  # Avoid very long texts
                    commentary_data["target_info"] = target_text
                    break
        
        print(f"Extracted commentary from {len(commentary_paragraphs)} commentary paragraphs")
        print(f"Found {len(recent_balls)} recent ball events")
        
    except Exception as e:
        print(f"Error parsing commentary HTML: {e}")
        # Enhanced fallback commentary
        fallback_text = f"Exciting cricket match in progress! Current score: {commentary_data['score'] or 'updating...'}"
        commentary_data["description"] = enhance_commentary_with_ai(fallback_text)
    
    return commentary_data

def crawl_commentary_data(url):
    """Crawl commentary data from the given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        commentary_data = extract_commentary_data_from_html(response.text)
        
        # Save the extracted data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(RESPONSE_FOLDER, f'scorecard_{timestamp}.json')
        
        with open(output_path, 'w') as f:
            json.dump(commentary_data, f, indent=2)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Commentary data saved: {output_path}")
        return True
        
    except requests.RequestException as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error fetching URL: {e}")
        return False
    except Exception as e:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing data: {e}")
        return False

def is_response_folder_empty(folder):
    """Check if the response folder is empty of JSON files."""
    return not any(f.lower().endswith('.json') for f in os.listdir(folder))

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting HTML commentary crawler...")
    print(f"Monitoring URL: {URL}")
    
    while True:
        # Only crawl if no JSON files exist in the folder
        if is_response_folder_empty(RESPONSE_FOLDER):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No recent data found. Crawling commentary data...")
            crawl_commentary_data(URL)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Recent data found, skipping crawl.")
        
        time.sleep(60)  # Wait 60 seconds before next check

if __name__ == "__main__":
    main()
