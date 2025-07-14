from db import models
from services import embeddings
from db import crud
import joblib
import logging
import os
import numpy as np


def relevant_articles(articles, threshold=0.55):
    """
    Vectorizes all articles at once and predicts relevance.
    Args:
        articles: (List[Article])
    Returns:
        List[bool]: Labels for each article (True = relevant)
        Embedded_articles : article embeddings
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models", "it_news_filter.joblib")
    classifier = joblib.load(MODEL_PATH)

    texts = []
    for article in articles:
        first_sentence = article.body.split(".")[0]
        texts.append(f"{article.title} {first_sentence}")

    embedded_articles = np.vstack([embeddings.embed_text(t) for t in texts])
    proba = classifier.predict_proba(embedded_articles)[:, 1]
    return proba >= threshold, embedded_articles

def importance_score(embedded_articles):
    """
    Args:
        articles: List[np.array]
    Returns :
        importance_score : importance score of the article
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models")

    # Score based on parameters
    params = ["severe", "wide_scope", "high_impact"]
    weights = {"severe" : 0.5, "wide_scope" : 0.3, "high_impact" : 0.2}
    scores = {}
    
    for param in params:
        clf = joblib.load(f"{MODEL_PATH}/{param}_model.joblib")
        y_prob = clf.predict_proba(embedded_articles)[:, 1]
        scores[param] = y_prob

    score = sum([weights[param]*scores[param] for param in params])

    return score

def freshness_score(articles):
    """
    Args:
        articles: (List[Article])
    Returns :
        importance_score : freshness score of the article
    """
    published = [datetime.fromisoformat(article['published_at'].replace("Z", "+00:00")) for article in articles]
    now_utc = dt.datetime.now(dt.timezone.utc)
    age_hours = (now_utc - published).total_seconds() / 3600
    tau_hours = 72
    freshness_score = math.exp(-age_hours / tau_hours)

    return freshness_score