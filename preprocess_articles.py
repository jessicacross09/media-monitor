import json
from rss_reader import fetch_articles, rss_url
from nlp_utils import analyze_article

def run_preprocessing():
    articles = fetch_articles(rss_url)
    processed = []

    for article in articles:
        tags = analyze_article(article['title'], article['summary'])
        article['people'] = ", ".join(tags.get('people', [])) or "-"
        article['leadership_terms'] = ", ".join(tags.get('leadership_terms', [])) or "-"
        article['aligned_with_us'] = tags.get('aligned_with_us', "No")
        article['matched_alignment_phrase'] = tags.get('matched_alignment_phrase', "-")
        article['reform_themes'] = ", ".join(tags.get('reform_themes', [])) or "-"
        processed.append(article)

    with open("data/processed_articles.json", "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_preprocessing()
