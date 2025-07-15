from db import models
from services import embeddings
from db import crud
import joblib
import logging
import os
import numpy as np
import datetime as dt



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
    MODEL_PATH = os.path.join(BASE_DIR, "models", "relevant_model.joblib")
    classifier = joblib.load(MODEL_PATH)

    texts = []
    for article in articles:
        first_sentence = article.body.split(".")[0]
        texts.append(f"{article.title} {first_sentence}")

    embedded_articles = np.vstack([embeddings.embed_text(t) for t in texts])
    proba = classifier.predict_proba(embedded_articles)[:, 1]
    return proba >= threshold, embedded_articles

def importance_score(articles, embedded_articles):
    """
    Args:
        articles: List[Article]
        embedded_articles : List[np.array]
    Returns :
        importance_score : importance score of the article
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_PATH = os.path.join(BASE_DIR, "models")

    # Score based on parameters
    params = ["severe", "wide_scope", "high_impact"]
    scores = {}
    
    for param in params:
        clf = joblib.load(f"{MODEL_PATH}/{param}_model.joblib")
        y_prob = clf.predict_proba(embedded_articles)[:, 1]
        scores[param] = y_prob

    for art, sev_score, wide_score, high_score in zip(articles, scores["severe"], scores["wide_scope"], scores["high_impact"]):
            art.severity_score = sev_score
            art.wide_scope_score = wide_score
            art.high_impact_score = high_score

    return articles

def freshness_score(articles):
    """
    Args:
        articles (List[dict]): List of article dictionaries with 'published_at'
    Returns:
        np.ndarray: Freshness scores for each article
    """
    def parse_utc(published_at):
        dt_obj = dt.datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        if dt_obj.tzinfo is None:
            return dt_obj.replace(tzinfo=dt.timezone.utc)
        return dt_obj

    published = np.array([parse_utc(article["published_at"]) for article in articles])
    now_utc = dt.datetime.now(dt.timezone.utc)
    age_hours = np.array([(now_utc - p).total_seconds() / 3600 for p in published])

    tau_hours = 72
    freshness_scores = np.exp(-age_hours / tau_hours)

    return freshness_scores