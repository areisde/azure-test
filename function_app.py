import azure.functions as func
#from api import crawl
#from api import ingest
#from api import retrieve
import json

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="crawl", methods=["GET"])
def crawl_and_process(req: func.HttpRequest) -> func.HttpResponse:
    try:
        #result = crawl.crawl_and_process()
        return func.HttpResponse(
        #    str(result),
            "Hello Crawler !",
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
"""
@app.route(route="ingest", methods=["POST"])
def ingest_articles(req: func.HttpRequest) -> func.HttpResponse:
    try:
        articles = req.get_json()
        success = ingest.ingest_articles(articles)
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
"""