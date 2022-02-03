from django.shortcuts import render
from elasticsearch_dsl.connections import get_connection
from .documents import Paper as PaperDocument
from ..utils.functions import normalize_es_response

es = get_connection()


def article_list(request):
    search_term = request.GET.get("term")
    year_from = request.GET.get("year_from")
    year_to = request.GET.get("year_to")

    query = {}
    if search_term:
        query = {
            "bool": {
                "should": [
                    {"match": {"title": search_term}},
                    {"match": {"snippet": search_term}},
                ],
            }
        }

    if year_from or year_to:
        if not query:
            query = {
                "bool": {
                    "filter": {
                        "range": {"publication.year": {}}
                    }
                }
            }
        else:
            query["bool"]["filter"] = {"range": {"publication.year": {}}}
        if year_from:
            query["bool"]["filter"]["range"]["publication.year"]["gte"] = year_from
        if year_to:
            query["bool"]["filter"]["range"]["publication.year"]["lte"] = year_to

    if query:
        search = es.search(index=PaperDocument.Index.name, query=query)
        papers = normalize_es_response(search["hits"]["hits"])
    else:
        papers = []
    return render(request, "article/list.html", {"papers": papers})


def article_detail(request, id):
    paper = normalize_es_response(es.get(index=PaperDocument.Index.name, id=id))
    if paper.get("citations"):
        paper["citations"] = normalize_es_response(
            es.mget(index=PaperDocument.Index.name, body={"ids": paper["citations"]})["docs"]
        )
    return render(request, "article/detail.html", {"paper": paper})
