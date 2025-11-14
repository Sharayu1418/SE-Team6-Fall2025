# SmartCache AI - Content Pool Collection

This directory contains scripts to collect content for SmartCache AI’s **content pool**. The scripts fetch data from YouTube, podcasts, and webpages based on a list of tags and save structured JSON files for later use.

---

## **Prerequisites**

- Python 3.12
- Virtual environment (`venv`) recommended
- Install dependencies:

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
pip install -r requirements.txt

# Collect YouTube videos
python scripts/collect_youtube.py

# Collect podcasts from RSS feeds
python scripts/collect_podcasts.py

# Collect webpages (Wikipedia + news)
python scripts/collect_webpages.py

