import json
import os
import urllib
from django.db.models.functions import Collate
from django.conf import settings

from .models import Person

DB_COLLATION = 'binary' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'en-x-icu'

PersonListViewQueryset = Person.objects.all().order_by(Collate("name", DB_COLLATION), Collate("first_name", DB_COLLATION))


class TypeSense_ExternalAutocomplete:
    def get_results(self, q):
        typesensetoken = os.getenv("TYPESENSE_TOKEN", None)
        typesenseserver = os.getenv("TYPESENSE_SERVER", None)
        if typesensetoken and typesenseserver and getattr(self, "collectionname"):
            url = f"{typesenseserver}/collections/{self.collectionname}/documents/search?q={q}&query_by=description&query_by=label"
            req = urllib.request.Request(url)
            req.add_header("X-TYPESENSE-API-KEY", typesensetoken)
            with urllib.request.urlopen(req) as f:
                data = json.loads(f.read())
                results = list(map(self.extract, data.get("hits", [])))
                return results
        return {}


class PlaceExternalAutocomplete(TypeSense_ExternalAutocomplete):
    collectionname = "prosnet-wikidata-place-index"

    def extract(self, res):
        url = res["document"]["id"]
        label = res["document"]["label"]
        if highlight := res.get("highlight"):
            if isinstance(highlight.get("label", {}), dict):
                label = highlight.get("label", {}).get("snippet", "")
        label += f' <a href="{url}">{url}</a>'
        return {
            "id": url,
            "text": label,
            "selected_text": label,
        }


class PersonExternalAutocomplete(TypeSense_ExternalAutocomplete):
    collectionname = "prosnet-wikidata-person-index"

    def extract(self, res):
        url = res["document"]["id"]
        label = res["document"]["label"]
        if highlight := res.get("highlight"):
            if isinstance(highlight.get("label", {}), dict):
                label = highlight.get("label", {}).get("snippet", "")
        label += f' <a href="{url}">{url}</a>'
        return {
            "id": url,
            "text": label,
            "selected_text": label,
        }
