import sys
import json
from bs4 import BeautifulSoup

def extract_last_over_commentary(html):
    soup = BeautifulSoup(html, "html.parser")
    commentary_blocks = soup.find_all("div", class_="cb-col cb-col-100 ng-scope")
    over_commentary = {}

    for block in commentary_blocks:
        over_div = block.find("div", class_="cb-mat-mnu-wrp cb-ovr-num ng-binding")
        comm_p = block.find("p", class_="cb-com-ln ng-binding ng-scope cb-col cb-col-90")
        if over_div and comm_p:
            over = over_div.get_text(strip=True)
            text = comm_p.get_text(strip=True)
            if over not in over_commentary:
                over_commentary[over] = []
            over_commentary[over].append(text)

    if not over_commentary:
        print("No commentary found.")
        return

    # Find the last over (max over number, e.g., 18.6 > 18.5 > 18.4 ...)
    def over_key(x):
        try:
            parts = x.split('.')
            return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)
        except Exception:
            return (0, 0)
    last_over = max(over_commentary.keys(), key=over_key)
    last_over_commentary = over_commentary[last_over]

    return {
        "last_over": last_over,
        "commentary": last_over_commentary
    }

if __name__ == "__main__":
    # Usage: python extract_last_over_commentary.py commentary_page.html
    if len(sys.argv) < 2:
        print("Usage: python extract_last_over_commentary.py commentary_page.html")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        html = f.read()

    result = extract_last_over_commentary(html)
    print(json.dumps(result, indent=2, ensure_ascii=False))
