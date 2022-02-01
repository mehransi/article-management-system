import os
import json
import inspect
from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand

from elasticsearch_dsl import Document


class Command(BaseCommand):
    def handle(self, *args, **options):
        installed_apps = settings.INSTALLED_APPS
        for app_name in installed_apps:
            if app_name.startswith("apps."):
                try:
                    document = import_module(f"{app_name}.documents")
                except:
                    continue
                for name, cls in inspect.getmembers(document):
                    if inspect.isclass(cls) and issubclass(cls, Document) and name != "Document":
                        cls.init()
