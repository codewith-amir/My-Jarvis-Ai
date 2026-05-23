# ============================================
# News Module
# Gets top headlines using RSS feed (no API key needed!)
# Uses BBC Urdu RSS which works well for Pakistan
# ============================================

import requests
import xml.etree.ElementTree as ET

def get_news():
    """Fetch top 5 news headlines from BBC RSS"""
    feeds = [
        ("BBC Urdu", "https://feeds.bbci.co.uk/urdu/rss.xml"),
        ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ]

    for source_name, url in feeds:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                continue

            root = ET.fromstring(response.content)
            items = root.findall(".//item")

            if not items:
                continue

            headlines = []
            for item in items[:5]:  # Top 5 headlines
                title_el = item.find("title")
                if title_el is not None and title_el.text:
                    headlines.append(title_el.text.strip())

            if headlines:
                result = f"📰 {source_name} - Aaj ki khabrein:\n\n"
                for i, h in enumerate(headlines, 1):
                    result += f"{i}. {h}\n"
                return result

        except requests.exceptions.ConnectionError:
            return "Internet nahi hai. News nahi aa sakti abhi."
        except Exception:
            continue

    return "News abhi available nahi. Baad mein try karo."
