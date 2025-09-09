import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from selenium.webdriver.common.by import By
import configparser
from PIL import Image
import io

config = configparser.ConfigParser()
config.read('config.properties')

IMAGE_FOLDER = config['DEFAULT']['SCORE_IMAGE_FOLDER']
URL = config['DEFAULT']['SCORE_URL']
Inns = config['DEFAULT']['INNS']

# crop values (pixels) - set in config.properties or defaults to 0
CROP_LEFT = int(config['DEFAULT'].get('CROP_LEFT', '0'))
CROP_RIGHT = int(config['DEFAULT'].get('CROP_RIGHT', '0'))
CROP_TOP = int(config['DEFAULT'].get('CROP_TOP', '0'))
CROP_BOTTOM = int(config['DEFAULT'].get('CROP_BOTTOM', '0'))

os.makedirs(IMAGE_FOLDER, exist_ok=True)

def take_scrolling_screenshot(url, save_folder):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })
    
    driver.get(url)
    time.sleep(2)

    # Set initial window size
    driver.set_window_size(1920, 1080)
    
    # Get total scroll height
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")
    
    # Take multiple screenshots
    screenshots = []
    offset = 0
    
    while offset < total_height:
        # Scroll to position
        driver.execute_script(f"window.scrollTo(0, {offset})")
        time.sleep(1)
        
        # Take screenshot
        screenshot = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
        screenshots.append(screenshot)
        
        offset += viewport_height
    
    # Create final stitched image
    total_width = screenshots[0].width
    total_height = sum(img.height for img in screenshots)
    
    stitched_image = Image.new('RGB', (total_width, total_height))
    current_height = 0
    
    for img in screenshots:
        stitched_image.paste(img, (0, current_height))
        current_height += img.height
    
    # Apply cropping based on config values
    width, height = stitched_image.size
    left = max(0, CROP_LEFT)
    top = max(0, CROP_TOP)
    right = max(left, width - CROP_RIGHT)
    bottom = max(top, height - CROP_BOTTOM)

    if right <= left or bottom <= top:
        # invalid crop, skip cropping
        cropped_image = stitched_image
        print("Crop values invalid or too large; saving full stitched image.")
    else:
        cropped_image = stitched_image.crop((left, top, right, bottom))
    
    # Save the final image
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    img_path = os.path.join(save_folder, f'scorecard_{timestamp}.png')
    cropped_image.save(img_path)
    
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
            take_scrolling_screenshot(URL, IMAGE_FOLDER)
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Existing image found, skipping screenshot.")
        time.sleep(60)

if __name__ == "__main__":
    main()