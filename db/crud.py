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


#def add_filter(filter_obj: models.Filter) -> bool:
#    """
#    Insert a filter into the filters table.
#    Args:
#        filter_obj (Filter): The filter object to insert.
#    Returns:
#        bool: True if insert was successful, False otherwise
#    """
#    try:
#
#        connection_string = os.environ.get("POSTGRES_CONNECTION_STRING")
#        vx = vecs.create_client(connection_string)
#        docs = vx.get_or_create_collection("filters", dimension=len(filter_obj.embedding))
#        vector = [(
#            filter_obj.url,
#            filter_obj.embedding.tolist(),
#            {"relevant": filter_obj.relevant}
#        )]
#        
#        docs.upsert(vector)
#        
#        return True
#    except Exception as e:
#        print(f"Error inserting filter: {e}")
#        return False


#def get_similar_articles(article_embedding) -> list:
#    """
#    Get similar articles based on the article embedding.
#    Args:
#        article_embedding (List[float]): The embedding of the article to check.
#    Returns:
#        List[Dict]: List of similar articles with keys: id, title, body, published_at
#    """
#    try:
#        connection_string = os.environ.get("POSTGRES_CONNECTION_STRING")
#        vx = vecs.create_client(connection_string)
#        docs = vx.get_collection("filters")
#        
#        results = docs.query(
#            data=article_embedding,
#            limit=100,
#            measure="cosine_distance",
#            include_value=True,
#            include_metadata=True,
#        )
#    except Exception as e:
#        print(f"Error fetching similar articles: {e}")
#        return []
#    
#    return results

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
                "importance_score": a.importance_score
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