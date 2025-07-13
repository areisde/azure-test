from services import filter
from db import models

def ingest_articles(articles):
    """
    Ingest a batch of raw article objects as a list of dicts.
    Each object must have id, source, title, body (optional), published_at.
    Returns True on success, False on error.
    """
    try:
        filtered_articles = []
        for article in articles:
            article_obj = models.Article(
                id=article.get("id"),
                source=article.get("source"),
                title=article.get("title"),
                body=article.get("body", ""),
                published_at=article.get("published_at"),
            )
            article = filter.filter_article(article_obj)
            filtered_articles.append(article)
        return filtered_articles
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}
    