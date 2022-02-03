from elasticsearch_dsl import Document, Text, Keyword, Date, Object, Nested


class User(Document):
    headline = Text()
    website = Keyword()
    avatar = Keyword()
    email_domain = Keyword()
    full_name = Text(required=True)
    memberships = Nested(
        properties={
            "start": Date(),
            "end": Date(),
            "role": Keyword(),
            "institute_id": Keyword(required=True)
        }
    )
    tags = Keyword(multi=True)

    class Index:
        name = "adb_users"
        settings = {
            "number_of_shards": 1,
        }


class PinnedPaper(Document):
    paper = Object(
        required=True, properties={"id": Keyword(required=True), "title": Text(required=True)}
    )
    user_id = Keyword(required=True)
    pinned_at = Date(required=True)

    class Index:
        name = "adb_pinned_papers"
        settings = {
            "number_of_shards": 1,
        }


class Institute(Document):
    name = Text(required=True)
    website = Keyword()
    logo = Keyword()
    established_at = Keyword(required=True)  # year

    class Index:
        name = "adb_institutes"
        settings = {
            "number_of_shards": 1,
        }


class Tag(Document):
    name = Keyword(required=True)

    class Index:
        name = "adb_tags"
        settings = {
            "number_of_shards": 1,
        }
