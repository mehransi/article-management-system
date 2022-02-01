
def _normalize_doc(doc):
    return {**doc["_source"], "id": doc["_id"], "score": doc.get("_score")}


def normalize_es_response(response):
    if type(response) == list:
        return list(map(_normalize_doc, response))
    return _normalize_doc(response)
