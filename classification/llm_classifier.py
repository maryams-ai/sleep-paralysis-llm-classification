# =============================================================
# Sleep Paralysis Narrative Classifier - Groq API version
# Classifies each narrative into: Intruder / Incubus / Vestibular-Motor / Other
# =============================================================
# HOW TO GET A GROQ API KEY (free):
# 1. Go to https://console.groq.com/keys
# 2. Sign in / sign up
# 3. Click "Create API Key" -> copy it
# 4. Paste it below in GROQ_API_KEY
#
# HOW TO USE:
# 1. Upload your FILTERED narratives CSV to Colab
#    (the 151-row one: sleep_paralysis_narratives_filtered_202.csv)
# 2. Check the exact uploaded filename in Colab's file panel and
#    update INPUT_CSV below to match EXACTLY (Colab sometimes adds
#    things like "(1)" to duplicate filenames)
# 3. Paste your API key below
# 4. Run this cell
# =============================================================

get_ipython().system('pip install groq pandas --quiet')

from groq import Groq
import pandas as pd
import time
import json
import re

# --- Settings: EDIT THESE ---
GROQ_API_KEY = "PASTE_YOUR_GROQ_API_KEY_HERE"
INPUT_CSV = "sleep_paralysis_narratives_filtered_202.csv"   # <-- MUST match your uploaded filename exactly (the 151-row filtered file)
OUTPUT_CSV = "sleep_paralysis_narratives_classified.csv"

client = Groq(api_key=GROQ_API_KEY)
MODEL_NAME = "openai/gpt-oss-120b"   # current Groq model - the old llama-3.1-70b-versatile was decommissioned

# --- The classification prompt, built from Cheyne's taxonomy ---
CLASSIFICATION_PROMPT = """You are helping classify first-person sleep paralysis narratives into a
research taxonomy from Cheyne et al. Read the narrative and classify it into
EXACTLY ONE of these four categories:

1. INTRUDER - The narrative centers on a sensed presence, or seeing/hearing
   a person, figure, demon, shadow being, or entity in the room. Fear is
   usually about "someone/something is here with me."

2. INCUBUS - The narrative centers on chest pressure, difficulty breathing,
   choking sensation, or a feeling of being crushed or suffocated, often
   combined with the sense of something sitting/pressing on the chest.

3. VESTIBULAR_MOTOR - The narrative centers on floating, flying,
   out-of-body sensations, spinning, falling, or a sense of movement/
   bodily displacement, without primary emphasis on a sensed intruder or
   chest pressure.

4. OTHER - The narrative does not clearly fit any of the above (e.g., pure
   confusion about whether it was sleep paralysis, general questions,
   sounds/vibrations without a clear intruder/incubus/vestibular element,
   or narratives combining unrelated themes).

Note: many narratives will show BOTH Intruder and Incubus elements together
(this is common and expected in the literature) - in that case, pick
whichever is more central/emphasized in the story. If truly balanced, use
"INTRUDER_INCUBUS" as the category.

Respond ONLY with a JSON object in this exact format, nothing else, no markdown:
{"category": "INTRUDER" or "INCUBUS" or "VESTIBULAR_MOTOR" or "INTRUDER_INCUBUS" or "OTHER", "reasoning": "one short sentence explaining why"}

Narrative to classify:
\"\"\"{narrative}\"\"\"
"""

def classify_narrative(text, retries=3):
    prompt = CLASSIFICATION_PROMPT.replace("{narrative}", text[:3000])  # cap length for safety

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,   # low temperature = more consistent classification
            )
            raw = response.choices[0].message.content.strip()

            # Strip markdown code fences if the model adds them
            raw = re.sub(r"^```json\s*|\s*```$", "", raw.strip())

            parsed = json.loads(raw)
            return parsed.get("category", "PARSE_ERROR"), parsed.get("reasoning", "")

        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(3)

    return "ERROR", "Failed after retries"

# --- Load data ---
df = pd.read_csv(INPUT_CSV)
print(f"Loaded {len(df)} narratives to classify.")

if len(df) > 160:
    print("WARNING: this looks like it might be the UNFILTERED file (should be ~151 rows). Double check INPUT_CSV filename!")

categories = []
reasonings = []

for i, row in df.iterrows():
    text = row["text_clean"]
    category, reasoning = classify_narrative(text)
    categories.append(category)
    reasonings.append(reasoning)

    print(f"[{i+1}/{len(df)}] {row['post_id']} -> {category}")

    time.sleep(1)  # small pause between calls

df["llm_category"] = categories
df["llm_reasoning"] = reasonings

df.to_csv(OUTPUT_CSV, index=False)
print(f"\nDone. Saved to {OUTPUT_CSV}")

# --- Quick summary ---
print("\nCategory distribution:")
print(df["llm_category"].value_counts())
