import feedparser
import json
from datetime import datetime
from textblob import TextBlob
import spacy

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# === RSS feeds ===
rss_feeds = {
    "APEC Newsroom": "https://www.apec.org/Press/News-Releases",
    "APEC Events Calendar": "https://www.apec.org/Press/Calendar",
    "U.S. Department of State – RSS": "https://www.state.gov/rss-feeds/",
    "U.S. Department of State – EAP": "https://www.state.gov/rss.xml",
    # U.S. Embassy Press Releases
    "U.S. Embassy – Canberra Press Releases": "https://au.usembassy.gov/tag/press-releases/feed/",
    "U.S. Embassy – Tokyo Press Releases": "https://jp.usembassy.gov/category/press-releases/feed/",
    "U.S. Embassy – Beijing Press Releases": "https://china.usembassy.gov/category/press-releases/feed/",
    "U.S. Embassy – Singapore Press Releases": "https://sg.usembassy.gov/category/press-releases/feed/",
    # (Add more U.S. Embassy feeds as needed)
    "Nikkei Asia": "https://asia.nikkei.com/rss",
    "The Diplomat": "https://thediplomat.com/feed/",
    "South China Morning Post": "https://www.scmp.com/rss",
    "Reuters Asia Pacific": "http://feeds.reuters.com/reuters/asiaPacificNews",
    "Channel News Asia": "https://www.channelnewsasia.com/rss",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "Lowy Institute": "https://www.lowyinstitute.org/rss.xml",
    "Google News – APEC Reforms": "https://news.google.com/rss/search?q=APEC+reform+digital+policy"
}

# === APEC economies for NER matching ===
APEC_ECONOMIES = [
    "Australia", "Brunei", "Canada", "Chile", "China", "Hong Kong",
    "Indonesia", "Japan", "South Korea", "Malaysia", "Mexico", "New Zealand",
    "Papua New Guinea", "Peru", "Philippines", "Russia", "Singapore",
    "Chinese Taipei", "Thailand", "United States", "Vietnam"
]

# === Map capitals and major cities to economies ===
CAPITAL_TO_ECONOMY = {
    "Canberra": "Australia",
    "Bandar Seri Begawan": "Brunei",
    "Ottowa": "Canada",
    "Santiago": "Chile",
    "Beijing": "China",
    "Jakarta": "Indonesia",
    "tokyo": "Japan",
    "Seoul": "Korea",
    "Kuala Lumpur": "Malaysia",
    "Mexico City": "Mexico",
    "Wellington": "New Zealand",
    "Port Moresby": "Papua New Guinea",
    "Manila": "Philippines",
    "Moscow": "Russia",
    "Bangkok": "Thailand",
    "washington": "United States",    
    "Hanoi": "Vietnam",
    # add other key cities as needed
}

# === Classification & Tagging Helpers ===
def classify_source(source_name):
    name = source_name.lower()
    if "embassy" in name or "consulate" in name:
        return "embassy"
    if "apec" in name or "state" in name:
        return "official"
    if "google news" in name:
        return "aggregator"
    return "media"

WORKSTREAM_KEYWORDS = {
    "Digital Trade": ["digital trade", "e-commerce", "data flow", "cross-border data", "digital economy"],
    "Cybersecurity": ["cybersecurity", "cyber attack", "data breach", "information security"],
    "Supply Chain Connectivity": ["supply chain", "logistics", "port", "shipping"],
    "Water Quality": ["water quality", "wastewater", "pollution", "sanitation"],
    "Technical Barriers to Trade": ["standards", "tbt", "technical regulation", "certification"],
    "Emerging Technology Standards": ["ai standards", "emerging technology", "artificial intelligence", "5g"]
}

ALIGNMENT_PHRASES = [
    "support from u.s.", "technical assistance", "aligned with apec goals",
    "strategic alignment", "bilateral cooperation", "u.s.-backed", "u.s.-supported",
    "partnership with the u.s.", "cooperation with the united states",
    "engagement with the united states", "funded by the united states"
]

NON_ALIGNMENT_PHRASES = [
    "not aligned", "no alignment", "not support", "no support",
    "without support", "not backed", "not supported", "disengaged from the united states",
    "opposed by the u.s.", "rejected by the u.s."
]

def detect_sentiment(text):
    pol = TextBlob(text).sentiment.polarity
    return "Positive" if pol > 0.1 else "Negative" if pol < -0.1 else "Neutral"

def detect_workstreams(text):
    txt = text.lower()
    hits = [ws for ws, kws in WORKSTREAM_KEYWORDS.items() if any(kw in txt for kw in kws)]
    return ", ".join(hits) if hits else "Uncategorized"

def detect_alignment(text):
    txt = text.lower()
    if any(phrase in txt for phrase in ALIGNMENT_PHRASES):
        return "Yes"
    if any(phrase in txt for phrase in NON_ALIGNMENT_PHRASES):
        return "No"
    return "Unclear"

def detect_economy(text):
    txt_lower = text.lower()
    for city, eco in CAPITAL_TO_ECONOMY.items():
        if city in txt_lower:
            return eco
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            for eco in APEC_ECONOMIES:
                if eco.lower() in ent.text.lower():
                    return eco
    return "Unknown"

articles = []
for source, url in rss_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        if not (title or summary):
            continue
        content = f"{title} {summary}"
        articles.append({
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
        })

# Write JSON file
with open("data/processed_articles.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)

print(f"✅ {len(articles)} articles written to data/processed_articles.json")

# === Risk Signal Aggregation for Scenario Simulator ===
risk_summary = defaultdict(lambda: {"score": 0, "justification": []})
for article in articles:
    econ = article["economy"]
    ws = article["workstreams"]
    if econ == "Unknown" or ws == "Uncategorized":
        continue
    for w in [w.strip() for w in ws.split(",")]:
        key = (econ, w)
        sentiment = article["sentiment"]
        alignment = article["aligned_with_us"]
        if sentiment == "Negative":
            risk_summary[key]["score"] -= 1
            risk_summary[key]["justification"].append("Negative sentiment")
        elif sentiment == "Positive":
            risk_summary[key]["score"] += 1
            risk_summary[key]["justification"].append("Positive sentiment")
        if alignment == "No":
            risk_summary[key]["score"] -= 1
            risk_summary[key]["justification"].append("Misalignment with U.S.")
        elif alignment == "Yes":
            risk_summary[key]["score"] += 1
            risk_summary[key]["justification"].append("U.S. cooperation")

records = []
for (eco, ws), data in risk_summary.items():
    score = data["score"]
    scenario = "Baseline"
    if score <= -2:
        scenario = "Pessimistic"
    elif score >= 2:
        scenario = "Optimistic"
    records.append({
        "Economy": eco,
        "Workstream": ws,
        "Scenario": scenario,
        "Justification": "; ".join(data["justification"])
    })

pd.DataFrame(records).to_csv("data/risk_signals.csv", index=False)
print("✅ risk_signals.csv written for scenario simulator.")

