from db import crud

def retrieve_events():
    """
    Retrieve all accepted events, sorted by published_at (descending).
    
    Returns:
        List[dict]: A list of event objects sorted by published_at in descending order.
    """
    try:
        articles_relevant = crud.get_articles()
        sorted_events = sorted(articles_relevant, key=lambda x: x['published_at'], reverse=True)
        return sorted_events
    except Exception as e:
        return {"error": f"An error occurred while retrieving events: {str(e)}"}


