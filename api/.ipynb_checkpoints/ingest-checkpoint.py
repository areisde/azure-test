from services import filter
from db import models
from db import crud
import logging

def ingest_articles(articles):
    """
    Ingest a batch of raw article objects as a list of dicts.
    Each object must have id, source, title, body (optional), published_at.
    Returns True on success, False on error.
    """
    logging.info("Ingesting articles...")
    try:
        article_objs = [
            models.Article(
                id=a.get("id"),
                source=a.get("source"),
                title=a.get("title"),
                body=a.get("body", ""),
                published_at=a.get("published_at"),
            )
            for a in articles
        ]

        logging.info("Filtering relevant articles...")
        labels, embedded_articles = filter.relevant_articles(article_objs)
        relevant_articles = [a for a, is_relevant in zip(article_objs, labels) if is_relevant ] # Keep only articles considered relevant
        relevant_articles_embedded = [emb_a for emb_a, is_relevant in zip(embedded_articles, labels) if is_relevant] # Same for the embeddings

        # Score importance
        importance_score = filter.importance_score(relevant_articles_embedded)
        freshness_score = filter.freshness_score(relevant_articles)

        logging.info("Uploading relevant articles to the database")
        crud.upload_articles(relevant_articles)

        return relevant_articles
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}
    