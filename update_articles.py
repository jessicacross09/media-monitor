import feedparser
import json
from datetime import datetime
from textblob import TextBlob
import spacy
import pandas as pd
from collections import defaultdict

# Load spaCy model for NER
nlp = spacy.load("en_core_web_sm")

# === RSS feeds ===
rss_feeds = {
    "APEC Newsroom": "https://www.apec.org/Press/News-Releases",
    "APEC Events Calendar": "https://www.apec.org/Press/Calendar",
    "U.S. Department of State – RSS": "https://www.state.gov/rss-feeds/",
    "U.S. Department of State – EAP": "https://www.state.gov/rss.xml",
    "U.S. Embassy – Canberra Press Releases": "https://au.usembassy.gov/tag/press-releases/feed/",
    "U.S. Embassy – Tokyo Press Releases": "https://jp.usembassy.gov/category/press-releases/feed/",
    "U.S. Embassy – Beijing Press Releases": "https://china.usembassy.gov/category/press-releases/feed/",
    "U.S. Embassy – Singapore Press Releases": "https://sg.usembassy.gov/category/press-releases/feed/",
    "Nikkei Asia": "https://asia.nikkei.com/rss",
    "The Diplomat": "https://thediplomat.com/feed/",
    "South China Morning Post": "https://www.scmp.com/rss",
    "Reuters Asia Pacific": "http://feeds.reuters.com/reuters/asiaPacificNews",
    "Channel News Asia": "https://www.channelnewsasia.com/rss",
    "Straits Times": "https://www.straitstimes.com/news/singapore/rss.xml",
    "CSIS – Asia Program": "https://www.csis.org/rss.xml",
    "Lowy Institute": "https://www.lowyinstitute.org/rss.xml",
    "Google News – APEC Reforms": "https://news.google.com/rss/search?q=APEC+reform+digital+policy"
}

APEC_ECONOMIES = [
    "Australia", "Brunei", "Canada", "Chile", "China", "Hong Kong",
    "Indonesia", "Japan", "South Korea", "Malaysia", "Mexico", "New Zealand",
    "Papua New Guinea", "Peru", "Philippines", "Russia", "Singapore",
    "Chinese Taipei", "Thailand", "United States", "Vietnam"
]

CAPITAL_TO_ECONOMY = {
    "canberra": "Australia",
    "washington": "United States",
    "tokyo": "Japan",
    "beijing": "China",
    "ottawa": "Canada",
    "jakarta": "Indonesia",
    "singapore": "Singapore",
    "kuala lumpur": "Malaysia",
    "bangkok": "Thailand",
    "manila": "Philippines",
    "wellington": "New Zealand",
    "mexico city": "Mexico",
    "port moresby": "Papua New Guinea"
}

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
    "Emerging Technology Standards": ["ai standards", "emerging technology", "artificial
