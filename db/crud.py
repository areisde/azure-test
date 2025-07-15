import os
from supabase import create_client
from . import models
import logging


def get_sources():
    """
    Query the 'sources' table and return all sources as a list of dicts.
    Returns:
        List[Dict]: List of sources with keys: id, name, url, type
    """
    sources = []
    
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if key and url:
            supabase = create_client(url, key)
            response = supabase.table('sources').select('*').execute()
            sources = response.data
    except Exception as e:
        # Log or handle error as needed
        print(f"Error fetching sources: {e}")
        
    return sources

def upload_articles(articles):
    """
    Upload a list of articles to the database using batch upsert.
    Args:
        articles (List[Article]): The list of articles to upload.
    Returns:
        bool: True if upload was successful, False otherwise.
    """
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not (key and url):
            return False

        supabase = create_client(url, key)

        payload = [
            {
                "id": a.id,
                "title": a.title,
                "body": a.body,
                "published_at": a.published_at,
                "source": a.source,
                "severity_score": a.severity_score,
                "wide_scope_score": a.wide_scope_score,
                "high_impact_score": a.high_impact_score
            }
            for a in articles
        ]

        supabase.table("articles").upsert(payload).execute()
        return True

    except Exception as e:
        print(f"Error batch uploading articles: {e}")
        return False
    
def get_articles():
    """
    Get all articles stored from the database.
    Returns:
        List[Dict]: List of articles with keys: id, title, body, published_at, source
    """
    try:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if key and url:
            supabase = create_client(url, key)
            response = supabase.table('articles').select('*').execute()
            return response.data
    except Exception as e:
        print(f"Error fetching articles: {e}")
        
    return []