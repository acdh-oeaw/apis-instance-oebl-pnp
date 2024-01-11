from django.core.management.base import BaseCommand
from django.db.models import Count

from apis_ontology.models import Person, Text, ProfessionCategory
from apis_highlighter.models import Annotation


class Command(BaseCommand):
    help = "Choose random people with annotations based on professioncategory"

    def handle(self, *args, **options):
        result = {}

        overall = Person.objects.exclude(professioncategory=None).count()
        # get ids of texts with more than 2 annotations
        text_ids = Annotation.objects.values("text_object_id").annotate(n=Count("pk")).filter(n__gt=2).values_list("text_object_id", flat=True)
        texts = Text.objects.filter(pk__in=text_ids)
        for professioncategory in ProfessionCategory.objects.all():
            result[professioncategory.name] = list()
            persons = Person.objects.filter(professioncategory=professioncategory)
            count = persons.count()
            perc = round(100 * count/overall)
            # print(f"{count} is {perc}% of {overall}")
            person_ids = persons.values_list("pk", flat=True)
            for i in range(perc):
                text = texts.filter(object_id__in=person_ids).order_by("?").first()
                result[professioncategory.name].append(text.content_object)

        for key in result:
            print(key)
            for val in result[key]:
                url = f"https://oebl-pnp.acdh-dev.oeaw.ac.at{val.get_absolute_url()}"
                url = url.replace("/detail/", "/edit/")
                print(f"{val},{url}")
