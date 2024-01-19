import django_filters
from apis_core.generic.filtersets import GenericFilterSet, GenericFilterSetForm

from apis_core.utils.filtermethods import (
    related_entity_name,
    related_property_name,
)
from .filters import trigram_search_filter

ABSTRACT_ENTITY_FILTERS_EXCLUDE = [
    "self_contenttype",
    "review",
    "start_date",
    "start_start_date",
    "start_end_date",
    "end_date",
    "end_start_date",
    "end_end_date",
    "notes",
    "text",
    "published",
    "status",
    "references",
]
HELP_TEXT = "Search for similar words in <em>first_name</em> & <em>name</em> based on <a href='https://www.postgresql.org/docs/current/pgtrgm.html#PGTRGM-CONCEPTS'>trigram matching</a>."


class PersonFilterSet(GenericFilterSet):
    related_entity_name = django_filters.CharFilter(
        method=related_entity_name, label="Related entity"
    )
    related_property_name = django_filters.CharFilter(
        method=related_property_name, label="Related property"
    )
    search = django_filters.CharFilter(
            method=trigram_search_filter,
            label="Trigram search",
            help_text=HELP_TEXT)

    class Meta:
        form = GenericFilterSetForm
        exclude = ABSTRACT_ENTITY_FILTERS_EXCLUDE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.move_to_end("first_name", False)
        self.filters.move_to_end("search", False)
