from db import crud
import logging

def retrieve_events():
    """
    Retrieve all accepted events, sorted by published_at (descending).
    
    Returns:
        List[dict]: A list of event objects sorted by published_at in descending order.
    """
    try:
        logging.info("Retrieving relevant articles...")
        articles_relevant = crud.get_articles()

        return articles_relevant
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}


