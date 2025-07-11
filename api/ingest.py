from typing import List
from db.crud import add_filter, get_similar_articles
from services.embeddings import embed_text
from services.filter import filter_article
from db.models import Article
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def ingest_articles(articles: List[dict]):
    """
    Ingest a batch of raw article objects as a list of dicts.
    Each object must have id, source, title, body (optional), published_at.
    Returns True on success, False on error.
    """
    try:
        process_articles(articles)
        return True
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return False


def process_articles(articles: List[dict]):
    """
    Process a list of articles by embedding and filtering them.
    Args:
        articles (List[dict]): List of article dicts to process.
    Returns:
        None
    """
    for article in articles:
        article_obj = Article(
            id=article.get("id"),
            source=article.get("source"),
            title=article.get("title"),
            body=article.get("body", ""),
            published_at=article.get("published_at"),
        )
        filter_article(article_obj)