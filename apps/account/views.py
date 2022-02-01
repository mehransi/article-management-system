from django.shortcuts import render
from elasticsearch_dsl.connections import get_connection
from apps.account.documents import User as UserDocument
from apps.article.documents import Paper as PaperDocument
from apps.utils.functions import normalize_es_response

es = get_connection()


def author_list_view(request):
    search_term = request.GET.get("term")
    if search_term:
        search = es.search(index=UserDocument.Index.name, query={
            "bool": {
                "should": [
                    {"match": {"full_name": search_term}},
                    {"match": {"headline": search_term}},
                    {"wildcard": {"full_name": f"*{search_term}*"}},
                ]
            }
        })
        authors = normalize_es_response(search["hits"]["hits"])
    else:
        authors = []

    return render(request, "account/author_list.html", {"authors": authors})


def author_detail_view(request, id):
    author = normalize_es_response(es.get(index=UserDocument.Index.name, id=id))
    papers_search = es.search(index=PaperDocument.Index.name, query={
        "nested": {"path": "authors", "query": {
            "term": {"authors.id": author["id"]}
        }}
    })
    author["papers"] = normalize_es_response(papers_search["hits"]["hits"])
    return render(request, "account/author_detail.html", {"author": author})
