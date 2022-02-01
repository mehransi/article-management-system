from elasticsearch_dsl import Document, Text, Keyword, Object, Nested, Integer


class Paper(Document):
    title = Text(required=True)
    keywords = Keyword(multi=True)
    snippet = Text()
    doi = Keyword()
    file = Keyword()
    references = Nested(
        required=True,
        properties={"paper_id": Keyword(required=True), "item": Keyword(required=True), "order": Integer(required=True)}
    )
    citations = Keyword(multi=True)  # list of ids of papers cited this paper
    authors = Nested(
        properties={
            "id": Keyword(), "full_name": Text(required=True), "order": Integer(required=True)
        }
    )
    publication = Object(
        properties={"title": Text(required=True), "year": Integer()}
    )

    class Index:
        name = "adb_papers"
        settings = {
            "number_of_shards": 1,
        }
