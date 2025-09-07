import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime

IMAGE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Images'
URL = "https://www.cricbuzz.com/live-cricket-scorecard/123677/wzone-vs-czone-2nd-semi-final-duleep-trophy-2025"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def take_screenshot(url, save_folder):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    img_path = os.path.join(save_folder, f'scorecard_{timestamp}.png')
    driver.save_screenshot(img_path)
    driver.quit()
    print(f"Screenshot saved: {img_path}")

def main():
    while True:
        take_screenshot(URL, IMAGE_FOLDER)
        time.sleep(60)

if __name__ == "__main__":
    main()