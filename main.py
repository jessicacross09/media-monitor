import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="📡 APEC-RISE Media Monitor", layout="wide")
st.title("📡 APEC-RISE Media Monitor")

# === Load data ===
@st.cache_data
def load_articles():
    with open("data/processed_articles.json", "r", encoding="utf-8") as f:
        return json.load(f)

articles = load_articles()

# === Ensure all expected fields exist ===
required_fields = [
    "title", "link", "published", "summary", "source", "source_type",
    "sentiment", "workstreams", "aligned_with_us", "economy", "timestamp"
]

for article in articles:
    for field in required_fields:
        article.setdefault(field, "Unknown")

df = pd.DataFrame(articles)

if df.empty:
    st.warning("No articles found.")
    st.stop()

# === Sidebar Filters ===
with st.sidebar:
    st.header("Filters")

    sentiments = ["All"] + sorted(df["sentiment"].dropna().unique().tolist())
    selected_sentiment = st.selectbox("Sentiment", sentiments)

    workstreams = ["All"] + sorted(df["workstreams"].dropna().unique().tolist())
    selected_workstream = st.selectbox("Workstream", workstreams)

    alignments = ["All"] + sorted(df["aligned_with_us"].dropna().unique().tolist())
    selected_alignment = st.selectbox("Aligned with U.S.", alignments)

    source_types = ["All"] + sorted(df["source_type"].dropna().unique().tolist())
    selected_type = st.selectbox("Source Type", source_types)

    # ✅ Static list of all APEC economies
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
    economies = ["All"] + apec_economies
    selected_economy = st.selectbox("Economy", economies)

# === Apply Filters ===
filtered_df = df.copy()

if selected_sentiment != "All":
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]

if selected_workstream != "All":
    filtered_df = filtered_df[filtered_df["workstreams"].str.contains(selected_workstream, na=False)]

if selected_alignment != "All":
    filtered_df = filtered_df[filtered_df["aligned_with_us"] == selected_alignment]

if selected_type != "All":
    filtered_df = filtered_df[filtered_df["source_type"] == selected_type]

if selected_economy != "All":
    filtered_df = filtered_df[filtered_df["economy"] == selected_economy]

# === Display Results ===
st.markdown(f"### Showing {len(filtered_df)} article(s)")

for _, row in filtered_df.iterrows():
    st.markdown(f"#### [{row['title']}]({row['link']})")
    st.markdown(f"**Source**: {row['source']} | **Published**: {row['published']}")
    st.markdown(f"**Economy**: {row['economy']} | **Sentiment**: {row['sentiment']} | **Workstreams**: {row['workstreams']} | **Alignment**: {row['aligned_with_us']} | **Type**: {row['source_type']}")
    st.markdown(f"{row['summary']}")
    st.markdown("---")

