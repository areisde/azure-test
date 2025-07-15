from db import crud
import logging
from services import filter
import os
import numpy as np

def retrieve_events():
    """
    Retrieve all accepted events, sorted by published_at (descending).
    
    Returns:
        List[dict]: A list of event objects sorted by published_at in descending order.
    """
    try:
        logging.info("Retrieving relevant articles...")
        # Fetch articles stored as relevant
        articles_relevant = crud.get_articles()

        # Rank those according to importance and freshness
        ranked_articles, scores = rank(articles_relevant)

        # Embed the score in the article dict
        articles_with_score = []
        for article, score in ranked_articles:
            article_copy = article.copy()  # avoid mutating original
            article_copy["score"] = score
            articles_with_score.append(article_copy)

        return articles_with_score
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}


def rank(articles):
    # Compute scores
    params = ["severity_score", "wide_scope_score", "high_impact_score"]
    scores = {}
    weights = {params[0] : os.environ.get("SEVERITY_WEIGHT"), params[1] : os.environ.get("WIDE_SCOPE_WEIGHT"), params[2]: os.environ.get("HIGH_IMPACT_WEIGHT")}
    scores[params[0]], scores[params[1]], scores[params[2]] = (np.array([a[param] for a in articles]) for param in params)
    importance_score = sum([float(weights[param])*scores[param] for param in params])
    freshness_score = filter.freshness_score(articles)
    final_score = float(os.environ.get("IMPORTANCE_WEIGHT"))*importance_score + float(os.environ.get("FRESHNESS_WEIGHT"))*freshness_score
    
    # Zip it back to articles
    scored_articles = list(zip(articles, final_score))
    ranked_articles = sorted(scored_articles, key=lambda x: x[1], reverse=True)

    return ranked_articles, final_score

