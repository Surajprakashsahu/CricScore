import requests
import configparser
import json
from bs4 import BeautifulSoup

def extract_last_n_balls_commentary(html, n=6):
    soup = BeautifulSoup(html, "html.parser")
    commentary_blocks = soup.find_all("div", class_="cb-col cb-col-100 ng-scope")
    ball_commentary = []

    for block in commentary_blocks:
        over_div = block.find("div", class_="cb-mat-mnu-wrp cb-ovr-num ng-binding")
        comm_p = block.find("p", class_="cb-com-ln ng-binding ng-scope cb-col cb-col-90")
        if over_div and comm_p:
            over = over_div.get_text(strip=True)
            text = comm_p.get_text(strip=True)
            ball_commentary.append({
                "over": over,
                "commentary": text
            })

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
    # Read config file to get CMTRY_URL
    config = configparser.ConfigParser()
    config.read("config.properties")
    cmtry_url = config.get("DEFAULT", "CMTRY_URL")

    print(f"Fetching commentary page from: {cmtry_url}")
    resp = requests.get(cmtry_url)
    resp.raise_for_status()
    commentary_html = resp.text

    # Extract last 6 balls commentary
    last_6 = extract_last_n_balls_commentary(commentary_html, n=6)
    if last_6 is not None:
        with open("last_6_balls_commentary.json", "w", encoding="utf-8") as f:
            json.dump(last_6, f, indent=2, ensure_ascii=False)
        print("Last 6 balls commentary saved to last_6_balls_commentary.json")
    else:
        print("No commentary extracted.")
