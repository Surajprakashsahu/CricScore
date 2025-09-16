

import requests
import json
import os
from bs4 import BeautifulSoup
import configparser


# --- LLM code skipped for now ---


def parse_scorecard_html(html):
    """
    Parse the scorecard HTML and return a structured dict with all relevant info.
    """

    soup = BeautifulSoup(html, "html.parser")
    innings_data = []
    for inn_div in soup.find_all("div", id=lambda x: x and x.startswith("innings_")):
        # Find the header for team name and score
        header = inn_div.find("div", class_="cb-scrd-hdr-rw")
        if not header:
            continue
        spans = header.find_all("span")
        team_name = spans[0].get_text(strip=True) if len(spans) > 0 else ""
        score = spans[1].get_text(strip=True) if len(spans) > 1 else ""

        batsmen = []
        extras = None
        total = None
        did_not_bat = []
        fow = []
        bowlers = []
        powerplays = []

        # Find all direct children after the header
        ltst_hdrs = inn_div.find_all("div", class_="cb-ltst-wgt-hdr", recursive=False)
        # Batting block is always the first cb-ltst-wgt-hdr
        if ltst_hdrs:
            bat_block = ltst_hdrs[0]
            # Batting rows
            for row in bat_block.find_all("div", class_="cb-scrd-itms", recursive=False):
                cols = row.find_all("div", recursive=False)
                # Batsman row
                if len(cols) >= 7 and cols[0].find("a"):
                    batsmen.append({
                        "name": cols[0].get_text(strip=True),
                        "dismissal": cols[1].get_text(strip=True),
                        "runs": cols[2].get_text(strip=True),
                        "balls": cols[3].get_text(strip=True),
                        "fours": cols[4].get_text(strip=True),
                        "sixes": cols[5].get_text(strip=True),
                        "sr": cols[6].get_text(strip=True)
                    })
                # Extras
                elif len(cols) >= 2 and "Extras" in cols[0].get_text():
                    extras = {
                        "total": cols[1].get_text(strip=True),
                        "breakdown": cols[2].get_text(strip=True) if len(cols) > 2 else ""
                    }
                # Total
                elif len(cols) >= 2 and "Total" in cols[0].get_text():
                    total = {
                        "total": cols[1].get_text(strip=True),
                        "info": cols[2].get_text(strip=True) if len(cols) > 2 else ""
                    }
                # Yet to Bat / Did not Bat
                elif len(cols) >= 2 and ("Yet to Bat" in cols[0].get_text() or "Did not Bat" in cols[0].get_text()):
                    did_not_bat = [a.get_text(strip=True) for a in cols[1].find_all("a")]

        # FOW block (after batting)
        fow_hdr = inn_div.find("div", class_="cb-scrd-sub-hdr", string=lambda s: s and "Fall of Wickets" in s)
        if fow_hdr:
            fow_row = fow_hdr.find_next_sibling("div")
            if fow_row:
                for span in fow_row.find_all("span"):
                    fow.append(span.get_text(strip=True))

        # Bowling block (second cb-ltst-wgt-hdr)
        if len(ltst_hdrs) > 1:
            bowl_block = ltst_hdrs[1]
            for row in bowl_block.find_all("div", class_="cb-scrd-itms", recursive=False):
                cols = row.find_all("div", recursive=False)
                if len(cols) >= 8 and cols[0].find("a"):
                    bowlers.append({
                        "name": cols[0].get_text(strip=True),
                        "overs": cols[1].get_text(strip=True),
                        "maidens": cols[2].get_text(strip=True),
                        "runs": cols[3].get_text(strip=True),
                        "wickets": cols[4].get_text(strip=True),
                        "nb": cols[5].get_text(strip=True),
                        "wd": cols[6].get_text(strip=True),
                        "eco": cols[7].get_text(strip=True)
                    })

        # Powerplays block (third cb-ltst-wgt-hdr or after bowling)
        # Find the cb-scrd-sub-hdr with Powerplays
        pp_hdr = inn_div.find("div", class_="cb-scrd-sub-hdr", string=lambda s: s and "Powerplays" in s)
        if pp_hdr:
            pp_row = pp_hdr.find_next_sibling("div")
            if pp_row:
                pp_cols = pp_row.find_all("div", recursive=False)
                if len(pp_cols) == 3:
                    powerplays.append({
                        "type": pp_cols[0].get_text(strip=True),
                        "overs": pp_cols[1].get_text(strip=True),
                        "runs": pp_cols[2].get_text(strip=True)
                    })

        innings_data.append({
            "team": team_name,
            "score": score,
            "batsmen": batsmen,
            "extras": extras,
            "total": total,
            "did_not_bat": did_not_bat,
            "fall_of_wickets": fow,
            "bowlers": bowlers,
            "powerplays": powerplays
        })

    # Match Info (outside innings)
    match_info = {}
    # Find the last cb-col cb-col-100 with cb-mtch-info-itm children
    info_sections = soup.find_all("div", class_="cb-col cb-col-100")
    for info_section in reversed(info_sections):
        if info_section.find("div", class_="cb-mtch-info-itm"):
            for itm in info_section.find_all("div", class_="cb-mtch-info-itm"):
                cols = itm.find_all("div", recursive=False)
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    val = cols[1].get_text(strip=True)
                    match_info[key] = val
            break

    return {
        "innings": innings_data,
        "match_info": match_info
    }



if __name__ == "__main__":
    # Read config file to get SCORE_URL
    config = configparser.ConfigParser()
    config.read("config.properties")
    score_url = config.get("DEFAULT", "SCORE_URL")

    # Fetch HTML from SCORE_URL
    print(f"Fetching scorecard from: {score_url}")
    resp = requests.get(score_url)
    resp.raise_for_status()
    scorecard_html = resp.text

    # Parse and extract scorecard data
    scorecard_json = parse_scorecard_html(scorecard_html)

    # Save to file in resource/score folder
    out_path = "resource/score/parsed_scorecard.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(scorecard_json, f, indent=2, ensure_ascii=False)
    print(f"Scorecard data saved to {out_path}")
