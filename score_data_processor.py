import os
import time
import json
import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.properties')

RESPONSE_FOLDER = config['DEFAULT']['SCORE_RESPONSE_FOLDER']

os.makedirs(RESPONSE_FOLDER, exist_ok=True)

def process_score_data(score_data):
    """Process and enhance score data."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing score data...")
    
    # Add processing timestamp
    score_data["processedAt"] = datetime.now().isoformat()
    
    # Calculate additional metrics
    try:
        current_score = score_data.get("liveDetails", {}).get("currentScore", {})
        runs = current_score.get("runs", 0)
        overs = current_score.get("overs", 0)
        balls = current_score.get("balls", 0)
        
        # Calculate current run rate
        if overs > 0 or balls > 0:
            total_balls = (overs * 6) + balls
            total_overs = total_balls / 6.0
            if total_overs > 0:
                current_run_rate = runs / total_overs
                score_data["liveDetails"]["currentScore"]["runRate"] = round(current_run_rate, 2)
        
        # Calculate required run rate if target is set
        target = current_score.get("target", 0)
        required = current_score.get("required", 0)
        
        if target > 0 and required > 0:
            # Assuming 50 overs match, calculate remaining overs
            remaining_overs = 50 - total_overs if total_overs < 50 else 0
            if remaining_overs > 0:
                required_run_rate = required / remaining_overs
                score_data["liveDetails"]["requiredRunRate"] = round(required_run_rate, 2)
        
        # Add match status
        if current_score.get("wickets", 0) >= 10:
            score_data["liveDetails"]["matchStatus"] = "innings_complete"
        elif required <= 0 and target > 0:
            score_data["liveDetails"]["matchStatus"] = "match_won"
        else:
            score_data["liveDetails"]["matchStatus"] = "live"
        
    except Exception as e:
        print(f"Error calculating metrics: {e}")
    
    return score_data

def safe_remove_file(file_path):
    """Safely remove a file and handle any potential errors."""
    try:
        os.remove(file_path)
        print(f"Successfully processed and removed {os.path.basename(file_path)}")
    except Exception as e:
        print(f"Error removing file {file_path}: {e}")

def process_new_data():
    """Process any new JSON data in the folder."""
    current_files = set(os.path.join(RESPONSE_FOLDER, f) for f in os.listdir(RESPONSE_FOLDER))
    new_files = current_files - processed
    
    if new_files:
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detected {len(new_files)} new score data file(s)")
    
    for fpath in new_files:
        if os.path.basename(fpath).lower().endswith('.json'):
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing score data: {os.path.basename(fpath)}")
                
                # Read the JSON data
                with open(fpath, 'r') as f:
                    score_data = json.load(f)
                
                # Process the data
                processed_data = process_score_data(score_data)
                
                # Save the processed data back
                with open(fpath, 'w') as f:
                    json.dump(processed_data, f, indent=2)
                
                processed.add(fpath)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Successfully processed score data: {os.path.basename(fpath)}")
                
                # Keep the file for further processing by other components
                # Don't remove it immediately like in the image-based version
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing {os.path.basename(fpath)}: {e}")
    
    return bool(new_files)

def main():
    global processed
    processed = set()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting score data processing service...")
    print(f"Monitoring folder: {RESPONSE_FOLDER}")
    
    last_check = 0
    check_interval = 30  # Regular check interval in seconds
    quick_check_interval = 5  # Quick check interval in seconds
    
    while True:
        current_time = time.time()
        
        if current_time - last_check >= check_interval:
            # Do a regular check and update the last check time
            found_new = process_new_data()
            last_check = current_time
            
            if not found_new:
                # If no new data, wait for the regular interval
                time.sleep(check_interval)
        else:
            # Do a quick check for new data
            if process_new_data():
                # If we found and processed new data, continue quick checking
                time.sleep(quick_check_interval)
            else:
                # If no new data in quick check, wait for the remainder of the regular interval
                remaining_time = check_interval - (time.time() - last_check)
                if remaining_time > 0:
                    time.sleep(remaining_time)
                else:
                    # If remaining time is negative, just do a quick sleep
                    time.sleep(quick_check_interval)

if __name__ == "__main__":
    main()
