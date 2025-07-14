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
        return ranked_articles
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}


def rank(articles):
    # Compute scores
    importance_score = np.array([a["importance_score"] for a in articles])
    freshness_score = filter.freshness_score(articles)
    final_score = float(os.environ.get("IMPORTANCE_WEIGHT"))*importance_score + float(os.environ.get("FRESHNESS_WEIGHT"))*freshness_score
    
    # Zip it back to articles
    scored_articles = list(zip(articles, final_score))
    ranked_articles = sorted(scored_articles, key=lambda x: x[1], reverse=True)

    return ranked_articles, final_score

