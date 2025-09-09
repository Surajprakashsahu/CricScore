import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.common.by import By
import configparser

config = configparser.ConfigParser()
config.read('config.properties')

IMAGE_FOLDER = config['DEFAULT']['IMAGE_FOLDER']
URL = config['DEFAULT']['CMTRY_URL']
Inns = config['DEFAULT']['INNS']

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
            if a.text.strip() == Inns:
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

def is_image_folder_empty(folder):
    """Check if the image folder is empty of PNG files."""
    return not any(f.lower().endswith('.png') for f in os.listdir(folder))

def main():
    while True:
        # Only take screenshot if no PNG files exist in the folder
        if is_image_folder_empty(IMAGE_FOLDER):
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No images found in folder. Taking new screenshot...")
            take_screenshot(URL, IMAGE_FOLDER)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Existing image found, skipping screenshot.")
        time.sleep(60)

if __name__ == "__main__":
    main()