import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import configparser
import json

config = configparser.ConfigParser()
config.read('config.properties')

RESPONSE_FOLDER = config['DEFAULT']['SCORE_RESPONSE_FOLDER']
URL = config['DEFAULT']['SCORE_URL']

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def extract_score_data_from_html(html_content):
    """Extract cricket score data from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    score_data = {
        "matchDetails": {
            "matchType": "",
            "venue": "",
            "series": "",
            "toss": {
                "winner": "",
                "decision": ""
            },
            "teams": {
                "team1": {
                    "id": "",
                    "name": "",
                    "flag": "",
                    "totalScore": ""
                },
                "team2": {
                    "id": "",
                    "name": "",
                    "flag": "",
                    "totalScore": ""
                }
            }
        },
        "liveDetails": {
            "battingTeam": "",
            "bowlingTeam": "",
            "currentScore": {
                "runs": 0,
                "wickets": 0,
                "overs": 0,
                "balls": 0,
                "target": 0,
                "required": 0,
                "runRate": 0
            },
            "batsmen": [],
            "bowler": {},
            "lastSixBalls": [],
            "thisOver": [],
            "winProbability": {
                "team1": 0,
                "team2": 0
            },
            "commentary": ""
        }
    }
    
    try:
        # Extract match title and series info - more specific selectors
        title_element = soup.find('title')
        if title_element:
            title_text = title_element.get_text(strip=True)
            score_data["matchDetails"]["series"] = title_text
            
            # Extract match type from title
            if "T20" in title_text.upper():
                score_data["matchDetails"]["matchType"] = "T20"
            elif "ODI" in title_text.upper():
                score_data["matchDetails"]["matchType"] = "ODI"
            elif "TEST" in title_text.upper():
                score_data["matchDetails"]["matchType"] = "Test"
        
        # Extract venue information - look for common venue patterns
        venue_selectors = [
            'div[class*="venue"]',
            'span[class*="venue"]',
            'div[class*="cb-nav-subhdr"]'
        ]
        
        for selector in venue_selectors:
            venue_element = soup.select_one(selector)
            if venue_element:
                venue_text = venue_element.get_text(strip=True)
                if 'at' in venue_text:
                    score_data["matchDetails"]["venue"] = venue_text.split('at')[-1].strip()
                elif len(venue_text) > 5 and len(venue_text) < 100:
                    score_data["matchDetails"]["venue"] = venue_text
                break
        
        # Extract team information - improved team detection
        team_selectors = [
            'div.cb-min-tm',
            'div[class*="team"]',
            'div.cb-col.cb-col-100.cb-font-18.cb-lst-itm-sm'
        ]
        
        teams = []
        for selector in team_selectors:
            team_elements = soup.select(selector)
            
            for i, team_elem in enumerate(team_elements[:2]):
                team_name_elem = team_elem.find(['div', 'span'], class_=lambda x: x and 'nm' in x) or team_elem.find(['div', 'span'])
                team_score_elem = team_elem.find(['div', 'span'], class_=lambda x: x and 'scr' in x)
                
                if not team_score_elem:
                    # Look for score in any child element
                    for child in team_elem.find_all(['div', 'span']):
                        text = child.get_text(strip=True)
                        if '/' in text and any(char.isdigit() for char in text):
                            team_score_elem = child
                            break
                
                team_name = team_name_elem.get_text(strip=True) if team_name_elem else ""
                team_score = team_score_elem.get_text(strip=True) if team_score_elem else ""
                
                if team_name or team_score:
                    team_id = team_name[:3].upper() if team_name else f"T{i+1}"
                    
                    teams.append({
                        "id": team_id,
                        "name": team_name,
                        "flag": "",
                        "totalScore": team_score
                    })
            
            if len(teams) >= 2:
                break
        
        if len(teams) >= 2:
            score_data["matchDetails"]["teams"]["team1"] = teams[0]
            score_data["matchDetails"]["teams"]["team2"] = teams[1]
        
        # Extract current batting details - improved score parsing
        current_score_selectors = [
            'div.cb-scr-wll-chse',
            'div[class*="cb-min-scr"]',
            'div[class*="score"]'
        ]
        
        for selector in current_score_selectors:
            current_score_elem = soup.select_one(selector)
            if current_score_elem:
                score_text = current_score_elem.get_text(strip=True)
                
                # Enhanced score parsing with regex
                import re
                score_pattern = r'(\d+)/?(\d*)\s*\((\d+)\.?(\d*)\s*(?:Ov|overs?)\)'
                match = re.search(score_pattern, score_text, re.IGNORECASE)
                
                if match:
                    runs = int(match.group(1))
                    wickets = int(match.group(2)) if match.group(2) else 0
                    overs = int(match.group(3))
                    balls = int(match.group(4)) if match.group(4) else 0
                    
                    score_data["liveDetails"]["currentScore"]["runs"] = runs
                    score_data["liveDetails"]["currentScore"]["wickets"] = wickets
                    score_data["liveDetails"]["currentScore"]["overs"] = overs
                    score_data["liveDetails"]["currentScore"]["balls"] = balls
                    break
        
        # Extract batsmen details - improved table parsing
        batsmen_selectors = [
            'table.cb-scrd-itms',
            'div[class*="batsman"]',
            'table[class*="scorecard"]'
        ]
        
        for selector in batsmen_selectors:
            batsmen_table = soup.select_one(selector)
            if batsmen_table:
                batsmen_rows = batsmen_table.find_all('tr')[1:] if batsmen_table.name == 'table' else batsmen_table.find_all('div')
                batsmen = []
                
                for row in batsmen_rows[:2]:  # Only current batsmen
                    cells = row.find_all(['td', 'div'])
                    if len(cells) >= 3:
                        name = cells[0].get_text(strip=True)
                        runs_text = cells[1].get_text(strip=True)
                        balls_text = cells[2].get_text(strip=True)
                        
                        # Extract numeric values
                        runs = 0
                        balls = 0
                        fours = 0
                        sixes = 0
                        
                        if runs_text.isdigit():
                            runs = int(runs_text)
                        if balls_text.isdigit():
                            balls = int(balls_text)
                        
                        # Look for fours and sixes in additional columns
                        if len(cells) > 3:
                            fours_text = cells[3].get_text(strip=True)
                            if fours_text.isdigit():
                                fours = int(fours_text)
                        if len(cells) > 4:
                            sixes_text = cells[4].get_text(strip=True)
                            if sixes_text.isdigit():
                                sixes = int(sixes_text)
                        
                        if name and name not in ['Total', 'Extras', 'Extra']:
                            batsman = {
                                "name": name,
                                "runs": runs,
                                "balls": balls,
                                "fours": fours,
                                "sixes": sixes,
                                "onStrike": len(batsmen) == 0  # First batsman is on strike
                            }
                            batsmen.append(batsman)
                
                if batsmen:
                    score_data["liveDetails"]["batsmen"] = batsmen
                    break
        
        # Extract toss information
        toss_patterns = [
            r'(\w+)\s+won\s+the\s+toss\s+and\s+chose\s+to\s+(bat|bowl)',
            r'(\w+)\s+won\s+the\s+toss.*?elected\s+to\s+(bat|bowl)'
        ]
        
        page_text = soup.get_text()
        for pattern in toss_patterns:
            import re
            toss_match = re.search(pattern, page_text, re.IGNORECASE)
            if toss_match:
                score_data["matchDetails"]["toss"]["winner"] = toss_match.group(1)
                score_data["matchDetails"]["toss"]["decision"] = toss_match.group(2).lower()
                break
        
        print(f"Extracted score data: {score_data['liveDetails']['currentScore']['runs']}/{score_data['liveDetails']['currentScore']['wickets']}")
        
    except Exception as e:
        print(f"Error parsing score HTML: {e}")
    
    return score_data

def crawl_score_data(url):
    """Crawl score data from the given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        score_data = extract_score_data_from_html(response.text)
        
        # Save the extracted data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(RESPONSE_FOLDER, f'scorecard_{timestamp}.json')
        
        with open(output_path, 'w') as f:
            json.dump(score_data, f, indent=2)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Score data saved: {output_path}")
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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting HTML score crawler...")
    print(f"Monitoring URL: {URL}")
    
    while True:
        # Only crawl if no JSON files exist in the folder
        if is_response_folder_empty(RESPONSE_FOLDER):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No recent data found. Crawling score data...")
            crawl_score_data(URL)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Recent data found, skipping crawl.")
        
        time.sleep(60)  # Wait 60 seconds before next check

if __name__ == "__main__":
    main()
