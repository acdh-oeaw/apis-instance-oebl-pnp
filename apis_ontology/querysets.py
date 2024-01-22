from dataclasses import dataclass
from django.db.models.functions import Collate
from django.conf import settings

from .models import Person

DB_COLLATION = 'binary' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'en-x-icu'

PersonListViewQueryset = Person.objects.all().order_by(Collate("name", DB_COLLATION), Collate("first_name", DB_COLLATION))


@dataclass
class AutocompleteItem:
    pk: str
    label: str

    def __str__(self):
        return self.label


def ProfessionCategoryAutocompleteQueryset(queryset, searchvalue):
    qs = queryset.objects.filter(name__icontains=searchvalue).values("name", "person")
    qs = [AutocompleteItem(pk=obj['person'], label=obj['name']) for obj in qs]
    return qs
