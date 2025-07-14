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
        labels = filter.relevant_articles(article_objs)
        relevant_articles = [a for a, is_relevant in zip(article_objs, labels) if is_relevant ]

        logging.info("Uploading relevant articles to the database")
        crud.upload_articles(relevant_articles)

        return relevant_articles
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}
    