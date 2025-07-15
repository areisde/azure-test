import azure.functions as func
from api import crawl
from api import ingest
from api import retrieve
import json
import logging

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.function_name(name="crawl_sources")
@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="mytimer")
def crawl_articles(mytimer: func.TimerRequest) -> None:
    logging.info("Running news crawler")
    results = crawl.crawl_and_process()
    logging.info(f"News crawler is done running and found {len(results)} relevant results")

@app.function_name(name="ingest_articles")
@app.route(route="ingest", methods=["POST"])
def ingest_articles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Try parsing as a regular JSON array
        try:
            articles = req.get_json()
            if not isinstance(articles, list):
                raise ValueError("Expected a list of articles")
        except (ValueError, json.JSONDecodeError):
            # Fallback: try to parse as NDJSON stream
            raw_body = req.get_body().decode("utf-8").strip()
            articles = []
            for i, line in enumerate(raw_body.splitlines(), start=1):
                try:
                    article = json.loads(line)
                    articles.append(article)
                except json.JSONDecodeError as e:
                    return func.HttpResponse(
                        json.dumps({"error": f"Invalid JSON on line {i}: {str(e)}"}),
                        status_code=400,
                        mimetype="application/json"
                    )

        # Check article structure
        for article in articles:
            if not isinstance(article, dict):
                return func.HttpResponse(
                    json.dumps({"error": "Each article must be a JSON object."}),
                    status_code=400,
                    mimetype="application/json"
                )
            required_keys = ["id", "source", "title", "published_at"]
            if not all(key in article for key in required_keys):
                return func.HttpResponse(
                    json.dumps({"error": f"Missing required keys in article: {article}"}),
                    status_code=400,
                    mimetype="application/json"
                )

        # Ingest articles
        result = ingest.ingest_articles(articles)

        return func.HttpResponse(
            json.dumps({"message": "Articles ingested successfully.", "count": len(result)}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Unexpected error during ingestion")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.function_name(name="retrieve_articles")
@app.route(route="retrieve", methods=["GET"])
def retrieve_articles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        result = retrieve.retrieve_events()
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
