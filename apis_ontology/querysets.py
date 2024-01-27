import json
import os
import urllib
from django.db.models.functions import Collate
from django.conf import settings

from .models import Person

DB_COLLATION = 'binary' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'en-x-icu'

PersonListViewQueryset = Person.objects.all().order_by(Collate("name", DB_COLLATION), Collate("first_name", DB_COLLATION))


class PersonExternalAutocomplete:

    def extract(self, res):
        return {
            "id": res["document"]["id"],
            "text": res["document"]["label"],
            "selected_text": res["document"]["label"]
        }

    def get_results(self, q):
        collectionname = "prosnet-wikidata-person-index"
        typesensetoken = os.getenv("TYPESENSE_TOKEN", None)
        typesenseserver = os.getenv("TYPESENSE_SERVER", None)
        if typesensetoken and typesenseserver:
            url = f"{typesenseserver}/collections/{collectionname}/documents/search?q={q}&query_by=description&query_by=label"
            req = urllib.request.Request(url)
            req.add_header("X-TYPESENSE-API-KEY", typesensetoken)
            with urllib.request.urlopen(req) as f:
                data = json.loads(f.read())
                results = list(map(self.extract, data.get("hits", [])))
                return results
        return {}
