# =============================================================
# Sleep Paralysis Narrative Scraper - NO API KEY NEEDED VERSION
# =============================================================
# HOW TO USE:
# 1. Go to https://colab.research.google.com and start a new notebook
# 2. Copy this whole file into a cell and run it
# 3. That's it - no Reddit account, no API keys, no CAPTCHA needed.
#
# HOW IT WORKS:
# Reddit exposes public post data as .json if you add "/.json" to
# any subreddit/listing URL. This pulls only PUBLIC posts, same
# as what anyone can see in a browser - no login required.
# We just have to be polite: slow requests + a proper User-Agent.
# =============================================================

get_ipython().system('pip install requests pandas --quiet')

import requests
import pandas as pd
import re
import time

# --- Settings ---
SUBREDDITS = ["Sleepparalysis"]   # add more later if needed, e.g. "Paranormal"
POSTS_PER_PAGE = 100              # Reddit's max per request
PAGES_TO_FETCH = 5                # 5 pages x 100 = up to 500 posts per subreddit
MIN_WORD_COUNT = 30                # skip very short posts

HEADERS = {
    "User-Agent": "sleep-paralysis-research-script (personal academic project)"
}

def clean_text(text):
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

rows = []

for sub_name in SUBREDDITS:
    after = None  # Reddit's pagination cursor
    print(f"Fetching from r/{sub_name} ...")

    for page in range(PAGES_TO_FETCH):
        url = f"https://www.reddit.com/r/{sub_name}/top.json?limit={POSTS_PER_PAGE}&t=all"
        if after:
            url += f"&after={after}"

        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"  Page {page+1}: request failed (status {response.status_code}). Stopping this subreddit.")
            break

        data = response.json()
        children = data.get("data", {}).get("children", [])

        if not children:
            print(f"  Page {page+1}: no more posts found.")
            break

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
                "subreddit": sub_name,
                "word_count": word_count,
                "text": full_text,
                "score": p.get("score"),
                "created_utc": p.get("created_utc"),
            })

        after = data.get("data", {}).get("after")
        print(f"  Page {page+1}: {len(children)} posts fetched, {len(rows)} total narratives so far.")

        if not after:
            break

        time.sleep(2)  # be polite to Reddit's servers - don't hammer requests

print(f"\nCollected {len(rows)} narratives before cleaning.")

# --- Build DataFrame and clean ---
df = pd.DataFrame(rows)
df["text_clean"] = df["text"].apply(clean_text)
df = df.drop_duplicates(subset="text_clean").reset_index(drop=True)

print(f"Final dataset size after cleaning: {len(df)} narratives")

# --- Save ---
df.to_csv("sleep_paralysis_narratives.csv", index=False)
print("Saved to sleep_paralysis_narratives.csv")

df.head(10)

# =============================================================
# NOTE: This method pulls Reddit's "top" posts (all time). If you
# want more variety, you can change "top.json" to "new.json" or
# "hot.json" and run it again, then combine the CSVs.
#
# NEXT STEP (separate script): feed df["text_clean"] to an LLM
# with the Cheyne taxonomy definitions to classify each narrative
# as Intruder / Incubus / V-M / Other.
# =============================================================
