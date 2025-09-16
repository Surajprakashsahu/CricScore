import requests
import configparser

if __name__ == "__main__":
    # Read config file to get CMTRY_URL
    config = configparser.ConfigParser()
    config.read("config.properties")
    cmtry_url = config.get("DEFAULT", "CMTRY_URL")

    print(f"Fetching commentary page from: {cmtry_url}")
    resp = requests.get(cmtry_url)
    resp.raise_for_status()
    commentary_html = resp.text

    # Save to file
    with open("commentary_page.html", "w", encoding="utf-8") as f:
        f.write(commentary_html)
    print("Commentary HTML saved to commentary_page.html")
