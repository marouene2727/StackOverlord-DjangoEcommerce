# utils.py
from transformers import pipeline

# Initialiser le pipeline d'analyse de sentiment
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_sentiment(text):
    try:
        result = sentiment_analyzer(text)[0]
        sentiment_label = result['label']
        sentiment_score = result['score']
        
        return sentiment_label, sentiment_score
    except Exception as e:
        print(f"Erreur lors de l'analyse de sentiment: {e}")
        return 'NEUTRAL', 0.0  # Valeur par défaut


def summarize_article(content, max_length=100):
    summarizer = pipeline("summarization")
    summary = summarizer(content, max_length=max_length, min_length=25, do_sample=False)
    return summary[0]['summary_text']