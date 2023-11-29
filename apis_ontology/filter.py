from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def fulltext_search_filter(queryset, name, value):
    return queryset.annotate(search=SearchVector("name", "first_name")).filter(search=SearchQuery(value))
