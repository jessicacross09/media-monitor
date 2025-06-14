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

# === Sidebar filters ===
st.sidebar.header("🔎 Filters")

economies = ["All"] + sorted(df["economy"].dropna().unique().tolist())
selected_economy = st.sidebar.selectbox("Filter by Economy", economies)

workstreams = ["All"] + sorted(df["workstreams"].dropna().unique().tolist())
selected_workstream = st.sidebar.selectbox("Filter by Workstream", workstreams)

sentiments = ["All"] + sorted(df["sentiment"].dropna().unique().tolist())
selected_sentiment = st.sidebar.selectbox("Filter by Sentiment", sentiments)

source_types = ["All"] + sorted(df["source_type"].dropna().unique().tolist())
selected_source_type = st.sidebar.selectbox("Filter by Source Type", source_types).

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

# === Apply filters ===
filtered_df = df.copy()
if selected_economy != "All":
    filtered_df = filtered_df[filtered_df["economy"] == selected_economy]
if selected_workstream != "All":
    filtered_df = filtered_df[filtered_df["workstreams"].str.contains(selected_workstream)]
if selected_sentiment != "All":
    filtered_df = filtered_df[filtered_df["sentiment"] == selected_sentiment]
if selected_source_type != "All":
    filtered_df = filtered_df[filtered_df["source_type"] == selected_source_type]
# === Show results ===
st.markdown(f"### Showing {len(filtered_df)} of {len(df)} articles")
for _, row in filtered_df.iterrows():
    st.markdown(f"""
    #### [{row['title']}]({row['link']})
    🗓️ {row['published']}  
    🌐 **Economy**: {row['economy']}  
    🧭 **Workstreams**: {row['workstreams']}  
    📊 **Sentiment**: {row['sentiment']}  
    📰 **Source**: {row['source']} ({row['source_type']})  
    
    > {row['summary']}
    ---
    """)
