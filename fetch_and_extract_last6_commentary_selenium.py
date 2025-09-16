import configparser
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_last_n_balls_commentary(driver, n=6):
    # Wait for commentary blocks to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.cb-col.cb-col-100.ng-scope"))
    )
    commentary_blocks = driver.find_elements(By.CSS_SELECTOR, "div.cb-col.cb-col-100.ng-scope")
    ball_commentary = []
    for block in commentary_blocks:
        try:
            over_div = block.find_element(By.CSS_SELECTOR, "div.cb-mat-mnu-wrp.cb-ovr-num.ng-binding")
            comm_p = block.find_element(By.CSS_SELECTOR, "p.cb-com-ln.ng-binding.ng-scope.cb-col.cb-col-90")
            over = over_div.text.strip()
            text = comm_p.text.strip()
            ball_commentary.append({
                "over": over,
                "commentary": text
            })
        except Exception:
            continue
    if not ball_commentary:
        print("No commentary found.")
        return None
    # Sort by over (descending: e.g., 18.6 > 18.5 > 18.4 ...)
    def over_key(x):
        try:
            parts = x["over"].split('.')
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except Exception:
            return (0, 0)
    ball_commentary.sort(key=over_key, reverse=True)
    last_n = ball_commentary[:n]
    return last_n

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.properties")
    cmtry_url = config.get("DEFAULT", "CMTRY_URL")
    inns_label = config.get("DEFAULT", "INNS")

    print(f"Fetching commentary page from: {cmtry_url}")
    print(f"Looking for INNS tab with label: {inns_label}")

    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(cmtry_url)

    # Wait for the <a> tag containing the INNS label and click it using user-provided logic
    try:
        a_tags = driver.find_elements(By.TAG_NAME, "a")
        found = False
        for a in a_tags:
            if a.text.strip() == inns_label:
                a.click()
                found = True
                time.sleep(1)  # Wait for content to update
                break
        if not found:
            print(f'No <a> tag with text "{inns_label}" found.')
    except Exception as e:
        print(f"Could not find or click INNS tab: {e}")

    # Extract last 6 balls commentary
    last_6 = extract_last_n_balls_commentary(driver, n=6)
    driver.quit()
    if last_6 is not None:
        out_path = "resource/cmtry/last_6_balls_commentary.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(last_6, f, indent=2, ensure_ascii=False)
        print(f"Last 6 balls commentary saved to {out_path}")
    else:
        print("No commentary extracted.")
