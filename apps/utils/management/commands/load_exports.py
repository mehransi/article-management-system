import os
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from elasticsearch import helpers
from elasticsearch_dsl.connections import get_connection


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("app_path", nargs=1, type=str)

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, options["app_path"][0] + "/fixture.json"), "r") as f:
            data = list(json.loads(f.read()))
        es = get_connection()

        for index_data in data:
            body = []
            for doc in index_data["documents"]:
                action = {"_index": index_data["index"], "_op_type": "create"}
                _id = doc.pop("id", None)
                if _id:
                    action["_id"] = _id
                action["_source"] = doc
                body.append(action)

            helpers.bulk(es, body)
