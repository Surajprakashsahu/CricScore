import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.common.by import By

IMAGE_FOLDER = '/Users/surabhibehera/Documents/Suraj/Projects/Gemma Projects/LiveStreaming/CricScore/Images'
URL = "https://www.cricbuzz.com/live-cricket-full-commentary/105794/eng-vs-rsa-3rd-odi-south-africa-tour-of-england-2025"

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def take_screenshot(url, save_folder):
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get(url)
    time.sleep(2)  # Wait for page to load

    # Find the third div inside nav and click it
    try:
        a_tags = driver.find_elements(By.TAG_NAME, "a")
        found = False
        for a in a_tags:
            if a.text.strip() == "RSA Inns":
                a.click()
                found = True
                time.sleep(1)  # Wait for content to update
                break
        if not found:
            print('No <a> tag with text "SLK Inns" found.')
    except Exception as e:
        print(f'Error clicking <a> tag with "SLK Inns": {e}')

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