# =============================================================
# Sleep Paralysis Narrative Parser - reads a manually downloaded
# Reddit JSON file (no live network request = no 403 block)
# =============================================================
# HOW TO GET THE JSON FILE:
# 1. In your own browser (not Colab), open:
#    https://www.reddit.com/r/Sleepparalysis/top.json?limit=100&t=all
# 2. Right-click the page -> "Save As" -> save it as reddit_data.json
#    (or copy all the text and paste into a plain text file, save
#    with a .json extension)
# 3. In Colab, click the folder icon on the left sidebar, then the
#    upload icon, and upload reddit_data.json
# 4. Run this script
#
# TO GET MORE PAGES:
# After running once, this script prints a "next_after" value at
# the end if there are more posts available. Go back to your
# browser and open:
#   https://www.reddit.com/r/Sleepparalysis/top.json?limit=100&t=all&after=PASTE_VALUE_HERE
# Save that as reddit_data_2.json, upload it, and add its filename
# to the FILES list below. Repeat for as many pages as you want.
# =============================================================

get_ipython().system('pip install pandas --quiet')

import json
import pandas as pd
import re

# --- List every JSON file you've uploaded so far ---
FILES = ["reddit_data.json"]   # add more filenames here as you collect more pages, e.g. ["reddit_data.json", "reddit_data_2.json"]

MIN_WORD_COUNT = 30

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

rows = []
next_after = None

for filename in FILES:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)

    children = data.get("data", {}).get("children", [])
    next_after = data.get("data", {}).get("after")

    for post in children:
        p = post["data"]
        title = p.get("title", "") or ""
        body = p.get("selftext", "") or ""
        full_text = f"{title}\n{body}".strip()

        word_count = len(full_text.split())
        if word_count < MIN_WORD_COUNT:
            continue

        rows.append({
            "post_id": p.get("id"),
            "subreddit": p.get("subreddit"),
            "word_count": word_count,
            "text": full_text,
            "score": p.get("score"),
            "created_utc": p.get("created_utc"),
        })

    print(f"{filename}: {len(children)} posts found in file, {len(rows)} narratives collected so far.")

if len(rows) == 0:
    print("\nNo narratives found. Check that your uploaded file actually contains Reddit JSON data")
    print("(open it and confirm it starts with something like {\"kind\": \"Listing\", \"data\": ...)")
else:
    df = pd.DataFrame(rows)
    df["text_clean"] = df["text"].apply(clean_text)
    df = df.drop_duplicates(subset="text_clean").reset_index(drop=True)

    print(f"\nFinal dataset size after cleaning: {len(df)} narratives")

    df.to_csv("sleep_paralysis_narratives.csv", index=False)
    print("Saved to sleep_paralysis_narratives.csv")

    if next_after:
        print(f"\nMore posts available. To get the next page, open this URL in your browser:")
        print(f"https://www.reddit.com/r/Sleepparalysis/top.json?limit=100&t=all&after={next_after}")
    else:
        print("\nNo more pages available - you've collected everything from 'top' this way.")

df.head(10) if len(rows) > 0 else None
