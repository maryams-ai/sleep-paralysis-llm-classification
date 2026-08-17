# Automated Classification of Sleep Paralysis Narratives

Comparing Western (Reddit) and South Asian sleep paralysis narratives using LLM-based classification against Cheyne et al.'s (1999) Intruder / Incubus / Vestibular-Motor taxonomy.

**Author:** Maryam Sadiq Bhatti, BS Artificial Intelligence, COMSATS University Islamabad, Lahore Campus

Full paper: [`paper/Sleep_Paralysis_Research_Paper_Bhatti.pdf`](paper/Sleep_Paralysis_Research_Paper_Bhatti.pdf)

## What this project does

Most narrative analysis of sleep paralysis relies on Western, Reddit-sourced data and manual qualitative coding. This project:

1. Collects first-person sleep paralysis narratives from r/Sleepparalysis using Reddit's public JSON endpoints (no API key required)
2. Collects a second sample from South Asian/Pakistani respondents via an anonymous survey
3. Classifies both samples using an LLM (Groq API, `openai/gpt-oss-120b`) against Cheyne's established hallucination taxonomy
4. Compares thematic distribution across the two samples

## Repository structure

```
data_collection/
  reddit_scraper.py       Attempts live scraping via Reddit's public JSON endpoints
  reddit_json_parser.py   Fallback parser for manually-downloaded JSON (used when Reddit
                           blocked cloud-hosted requests with HTTP 403 errors)
classification/
  llm_classifier.py       Classifies narratives into Intruder / Incubus / Vestibular-Motor /
                           Intruder_Incubus / Other using Groq's LLM API
data/
  reddit_narratives_classified.csv       151 filtered, classified Reddit narratives
  south_asian_narratives_classified.csv  16 filtered, classified South Asian narratives
paper/
  Sleep_Paralysis_Research_Paper_Bhatti.pdf   Full write-up
```

## Key findings

- Intruder was the most common hallucination category in both samples (49.0% Reddit, 37.5% South Asian)
- A recurring "Auditory/Vibrational" pattern emerged in both samples that falls outside Cheyne's original three categories
- The South Asian sample showed proportionally more Incubus and Vestibular-Motor classifications than the Reddit sample
- Recruiting South Asian participants was considerably harder than expected, likely reflecting cultural discomfort discussing an experience associated with jinn and supernatural meaning, even under full anonymity

## Notes on method

Reddit's official API (PRAW) could not be used due to persistent CAPTCHA failures during app registration. Direct unauthenticated requests from a cloud-hosted notebook were blocked with HTTP 403 errors, likely due to rate-limiting of data-center IP traffic. The working approach retrieves Reddit's public JSON pages through a normal browser session and parses them locally.

## Limitations

The South Asian sample (n=16) is much smaller than the Reddit sample (n=151) and should be read as exploratory. Full limitations are discussed in the paper.

## License

Code is shared for transparency and reproducibility. Please cite the paper if you build on this work.
