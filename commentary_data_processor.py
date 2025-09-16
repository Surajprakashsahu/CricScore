import os
import time
import json
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.properties')

RESPONSE_FOLDER = config['DEFAULT']['RESPONSE_FOLDER']

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def enhance_commentary_data(commentary_data):
    """Enhance commentary data with additional processing."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enhancing commentary data...")
    
    # Add processing timestamp
    commentary_data["processedAt"] = datetime.now().isoformat()
    
    try:
        # Enhance the description for better TTS
        description = commentary_data.get("description", "")
        score = commentary_data.get("score", "")
        
        # Create a more engaging commentary
        if description and score:
            enhanced_description = f"Current score is {score}. {description}"
        elif score:
            enhanced_description = f"The current score stands at {score}. Exciting cricket action continues!"
        elif description:
            enhanced_description = description
        else:
            enhanced_description = "Live cricket match in progress with thrilling action on the field!"
        
        # Add excitement words based on recent balls
        recent_balls = commentary_data.get("recentBalls", [])
        excitement_level = 0
        
        for ball in recent_balls:
            if ball.get("type") == "six":
                excitement_level += 3
            elif ball.get("type") == "four":
                excitement_level += 2
            elif ball.get("type") == "wicket":
                excitement_level += 4
        
        # Add excitement phrases
        if excitement_level >= 6:
            enhanced_description = f"What an incredible over! {enhanced_description}"
        elif excitement_level >= 3:
            enhanced_description = f"Exciting action! {enhanced_description}"
        
        commentary_data["description"] = enhanced_description
        commentary_data["excitementLevel"] = excitement_level
        
        # Add ball summary
        if recent_balls:
            ball_summary = []
            for ball in recent_balls[:6]:  # Last 6 balls
                ball_type = ball.get("type", "unknown")
                runs = ball.get("runs", 0)
                
                if ball_type == "six":
                    ball_summary.append("SIX!")
                elif ball_type == "four":
                    ball_summary.append("FOUR!")
                elif ball_type == "wicket":
                    ball_summary.append("WICKET!")
                elif ball_type == "dot":
                    ball_summary.append("dot")
                else:
                    ball_summary.append(str(runs))
            
            if ball_summary:
                commentary_data["lastSixBalls"] = ball_summary
                ball_summary_text = ", ".join(ball_summary)
                commentary_data["description"] += f" The last few balls: {ball_summary_text}."
        
        # Add over progression
        if "currentOver" in commentary_data:
            over_info = commentary_data["currentOver"]
            commentary_data["description"] += f" Currently in over {over_info}."
        
        # Add target information if available
        if "target_info" in commentary_data:
            target_info = commentary_data["target_info"]
            commentary_data["description"] += f" {target_info}."
        
    except Exception as e:
        print(f"Error enhancing commentary: {e}")
        # Fallback to basic commentary
        if "description" not in commentary_data or not commentary_data["description"]:
            commentary_data["description"] = "Live cricket match continues with exciting action!"
    
    return commentary_data

def safe_remove_file(file_path):
    """Safely remove a file and handle any potential errors."""
    try:
        os.remove(file_path)
        print(f"Successfully processed and removed {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error removing file {file_path}: {e}")

def process_new_commentary():
    """Process any new commentary JSON data in the folder."""
    current_files = set(os.path.join(RESPONSE_FOLDER, f) for f in os.listdir(RESPONSE_FOLDER))
    new_files = current_files - processed
    
    if new_files:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detected {len(new_files)} new commentary file(s)")
    
    for fpath in new_files:
        if os.path.basename(fpath).lower().endswith('.json'):
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing commentary: {os.path.basename(fpath)}")
                
                # Read the JSON data
                with open(fpath, 'r') as f:
                    commentary_data = json.load(f)
                
                # Enhance the commentary data
                enhanced_data = enhance_commentary_data(commentary_data)
                
                # Save the enhanced data back
                with open(fpath, 'w') as f:
                    json.dump(enhanced_data, f, indent=2)
                
                processed.add(fpath)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully enhanced commentary: {os.path.basename(fpath)}")
                
                # Keep the file for TTS processing
                # The generateCommentry.py will pick it up for audio generation
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing {os.path.basename(fpath)}: {e}")
    
    return bool(new_files)

def main():
    global processed
    processed = set()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting commentary data processing service...")
    print(f"Monitoring folder: {RESPONSE_FOLDER}")
    
    last_check = 0
    check_interval = 30  # Regular check interval in seconds
    quick_check_interval = 5  # Quick check interval in seconds
    
    while True:
        current_time = time.time()
        
        if current_time - last_check >= check_interval:
            # Do a regular check and update the last check time
            found_new = process_new_commentary()
            last_check = current_time
            
            if not found_new:
                # If no new commentary, wait for the regular interval
                time.sleep(check_interval)
        else:
            # Do a quick check for new commentary
            if process_new_commentary():
                # If we found and processed new commentary, continue quick checking
                time.sleep(quick_check_interval)
            else:
                # If no new commentary in quick check, wait for the remainder of the regular interval
                remaining_time = check_interval - (time.time() - last_check)
                if remaining_time > 0:
                    time.sleep(remaining_time)
                else:
                    # If remaining time is negative, just do a quick sleep
                    time.sleep(quick_check_interval)

if __name__ == "__main__":
    main()
