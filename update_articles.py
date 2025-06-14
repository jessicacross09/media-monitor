import feedparser
import json
from datetime import datetime
from textblob import TextBlob
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# APEC economies and aliases
APEC_ECONOMIES = {
"Australia": ["australia", "canberra"],
    "Brunei": ["brunei", "bandar seri begawan"],
    "Canada": ["canada", "ottawa", "canadian"],
    "Chile": ["chile", "santiago"],
    "China": ["china", "beijing", "prc", "chinese"],
    "Hong Kong, China": ["hong kong", "hk"],
    "Indonesia": ["indonesia", "jakarta"],
    "Japan": ["japan", "tokyo"],
    "Korea": ["korea", "south korea", "seoul", "rok"],
    "Malaysia": ["malaysia", "kuala lumpur"],
    "Mexico": ["mexico", "mexican"],
    "New Zealand": ["new zealand", "wellington"],
    "Papua New Guinea": ["papua new guinea", "png", "port moresby"],
    "Peru": ["peru", "lima"],
    "Philippines": ["philippines", "manila"],
    "Russia": ["russia", "moscow"],
    "Singapore": ["singapore"],
    "Chinese Taipei": ["taiwan", "taipei", "chinese taipei"],
    "Thailand": ["thailand", "bangkok"],
    "United States": ["united states", "usa", "u.s.", "washington", "american"],
    "Vietnam": ["vietnam", "hanoi"]
}

def detect_economy(text):
    for eco in APEC_ECONOMIES:
        if eco.lower() in text.lower():
            return eco
    return "Unknown"

# === RSS Feeds ===
rss_feeds = {
    # Official & Government
    "APEC Newsroom": "https://www.apec.org/Press/News-Releases",
    "APEC Events Calendar": "https://www.apec.org/Press/Calendar",
    "U.S. Department of State – EAP": "https://www.state.gov/rss.xml",

    # Media
    "Nikkei Asia": "https://asia.nikkei.com/rss",
    "The Diplomat": "https://thediplomat.com/feed/",
    "South China Morning Post": "https://www.scmp.com/rss",
    "Reuters Asia Pacific": "http://feeds.reuters.com/reuters/asiaPacificNews",
    "Channel News Asia": "https://www.channelnewsasia.com/rss",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",

    # Think Tanks
    "CSIS – Asia Program": "https://www.csis.org/rss.xml",
    "Lowy Institute": "https://www.lowyinstitute.org/rss.xml",

    # Aggregator
    "Google News – APEC Reforms": "https://news.google.com/rss/search?q=APEC+reform+digital+policy",

    # U.S. Embassies (APEC)
    "U.S. Embassy Australia": "https://au.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Brunei": "https://bn.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Canada": "https://ca.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Chile": "https://cl.usembassy.gov/category/alert/feed/",
    "U.S. Embassy China": "https://china.usembassy.gov/category/alert/feed/",
    "U.S. Consulate Hong Kong": "https://hk.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Indonesia": "https://id.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Japan": "https://jp.usembassy.gov/category/alert/feed/",
    "U.S. Embassy South Korea": "https://kr.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Malaysia": "https://my.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Mexico": "https://mx.usembassy.gov/category/alert/feed/",
    "U.S. Embassy New Zealand": "https://nz.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Papua New Guinea": "https://pg.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Peru": "https://pe.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Philippines": "https://ph.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Russia": "https://ru.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Singapore": "https://sg.usembassy.gov/category/alert/feed/",
    "AIT Taiwan (unofficial)": "https://tw.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Thailand": "https://th.usembassy.gov/category/alert/feed/",
    "U.S. Embassy Vietnam": "https://vn.usembassy.gov/category/alert/feed/"
}

# === Classify by source type ===
def classify_source(source_name):
    if "embassy" in source_name.lower() or "consulate" in source_name.lower():
        return "Government"
    elif "apec" in source_name.lower() or "state" in source_name.lower():
        return "Official"
    elif "google news" in source_name.lower():
        return "Aggregator"
    else:
        return "Media"

# === NLP Tagging Rules ===
WORKSTREAM_KEYWORDS = {
    "Digital Trade": ["digital trade", "e-commerce", "data flow", "cross-border data", "digital economy", "online platforms"],
    "Cybersecurity": ["cybersecurity", "cyber attack", "data breach", "information security", "digital threat"],
    "Supply Chain Connectivity": ["supply chain", "logistics", "port", "transport", "shipping", "infrastructure"],
    "Water Quality": ["water quality", "wastewater", "pollution", "clean water", "sanitation"],
    "Technical Barriers to Trade": ["standards", "TBT", "technical regulation", "compliance", "certification"],
    "Emerging Technology Standards": ["AI standards", "emerging technology", "artificial intelligence", "5G", "quantum computing"]
}

ALIGNMENT_PHRASES = [
    "Support from U.S.", "Technical Assistance", "Aligned with U.S. Goals",
    "Strategic Alignment","Bilateral Cooperation", "U.S.-Backed",
    "U.S.-Supported", "In Collaboration with U.S."
]

def detect_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive"
    elif polarity < -0.1:
        return "Negative"
    return "Neutral"

def detect_workstreams(text):
    matches = []
    for stream, keywords in WORKSTREAM_KEYWORDS.items():
        if any(kw.lower() in text.lower() for kw in keywords):
            matches.append(stream)
    return ", ".join(matches) if matches else "Uncategorized"

def detect_alignment(text):
    for phrase in ALIGNMENT_PHRASES:
        if phrase.lower() in text.lower():
            return "Yes"
    return "Unclear"

def detect_economy(text):
    text = text.lower()
    for economy, aliases in APEC_ECONOMIES.items():
        for alias in aliases:
            if alias in text:
                return economy
    return "Unknown"

# Parse feeds
articles = []
feed_count = 0
for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    feed_count += 1
    print(f"📡 {source}: {len(feed.entries)} entries")
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        if not title or not summary:
            continue
        content = f"{title} {summary}"

        article = {
            "title": title,
            "link": entry.get("link", "").strip(),
            "published": entry.get("published", ""),
            "summary": summary,
            "source": source,
            "source_type": classify_source(source),
            "sentiment": detect_sentiment(content),
            "workstreams": detect_workstreams(content),
            "aligned_with_us": detect_alignment(content),
            "economy": detect_economy(content),
            "timestamp": datetime.utcnow().isoformat()
        }
        articles.append(article)

# Save
with open("data/processed_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"✅ Total articles written: {len(articles)} from {feed_count} feeds")
