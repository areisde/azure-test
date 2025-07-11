import azure.functions as func
from api.crawl import crawl_and_process
from api.ingest import ingest_articles
import json
from api.retrieve import retrieve_events

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.function_name(name="CrawlAndProcess")
@app.route(route="api/crawl", methods=["GET"])
def crawl_and_process(req: func.HttpRequest) -> func.HttpResponse:
    try:
        result = crawl_and_process()
        return func.HttpResponse(
            str(result),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )

@app.function_name(name="IngestArticles")
@app.route(route="api/ingest", methods=["POST"])
def ingest_articles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        articles = req.get_json()
        success = ingest_articles(articles)
        if success:
            return func.HttpResponse(
                json.dumps({"message": "Articles ingested successfully."}),
                status_code=200,
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"error": "Error ingesting articles."}),
                status_code=400,
                mimetype="application/json"
            )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=400,
            mimetype="application/json"
        )

@app.function_name(name="RetrieveArticles")
@app.route(route="api/retrieve", methods=["GET"])
def retrieve_articles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        result = retrieve_events()
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
