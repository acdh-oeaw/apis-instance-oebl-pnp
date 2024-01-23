from apis_acdhch_default_settings.settings import *
from apis_ontology.filters import trigram_search_filter

DEBUG = True

INSTALLED_APPS += ["apis_highlighter", "django.contrib.postgres", "apis_core.collections"]
INSTALLED_APPS.remove("apis_ontology")
INSTALLED_APPS.insert(0, "apis_ontology")

ROOT_URLCONF = 'apis_ontology.urls'

PROJECT_DEFAULT_MD = {}

CSRF_TRUSTED_ORIGINS = ["https://oebl-pnp.acdh-dev.oeaw.ac.at"]


APIS_ENTITIES = {
        "Person": {
            "list_filters": {
                "name": {"method": trigram_search_filter, "label": "Name or first name"},
            },
        },
}

APIS_LIST_LINKS_TO_EDIT = True
