import spacy
from spacy.cli import download
import streamlit as st

@st.cache_resource(show_spinner=False)
def get_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

nlp = get_nlp_model()

LEADERSHIP_TERMS = ["minister", "secretary", "director", "commissioner"]
US_OBJECTIVES = ["trade facilitation", "digital economy", "regulatory reform", "supply chain resilience"]
REFORM_THEMES = ["customs", "digital", "infrastructure", "investment", "logistics", "interoperability"]

def analyze_article(title, summary):
    doc = nlp(title + " " + summary)
    people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    text = doc.text.lower()

    leadership_terms = [term for term in LEADERSHIP_TERMS if term in text]
    matched_alignment = next((obj for obj in US_OBJECTIVES if obj in text), None)
    reform_themes = [theme for theme in REFORM_THEMES if theme in text]

    return {
        "people": people,
        "leadership_terms": leadership_terms,
        "aligned_with_us": "Yes" if matched_alignment else "No",
        "matched_alignment_phrase": matched_alignment or "-",
        "reform_themes": reform_themes,
    }


