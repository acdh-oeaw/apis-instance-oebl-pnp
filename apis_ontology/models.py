import reversion
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from apis_core.apis_entities.models import AbstractEntity
from apis_core.core.models import LegacyDateMixin
from apis_core.utils import DateParser


class LegacyStuffMixin(models.Model):
    review = review = models.BooleanField(default=False, help_text="Should be set to True, if the data record holds up quality standards.")
    status = models.CharField(max_length=100, blank=True)
    references = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    texts = GenericRelation("Text")
    sources = GenericRelation("Source")

    class Meta:
        abstract = True


@reversion.register
class Source(models.Model):
    orig_filename = models.CharField(max_length=255, blank=True)
    indexed = models.BooleanField(default=False)
    pubinfo = models.CharField(max_length=400, blank=True)
    author = models.CharField(max_length=255, blank=True)
    orig_id = models.PositiveIntegerField(blank=True, null=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        if self.author and self.orig_filename:
            return f"{self.orig_filename}, stored by {self.author}"
        return f"(ID: {self.id})".format(self.id)


@reversion.register
class Title(models.Model):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


@reversion.register
class ProfessionCategory(models.Model):
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name


@reversion.register
class Profession(models.Model):
    class Meta:
        ordering = ("name",)

    name = models.CharField(max_length=255, blank=True)
    oldids = models.TextField(null=True)
    oldnames = models.TextField(null=True)

    def __str__(self):
        return self.name or f"No name ({self.id})"


@reversion.register(follow=["rootobject_ptr"])
class Event(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    kind = models.CharField(max_length=255, blank=True, null=True)


@reversion.register(follow=["rootobject_ptr"])
class Institution(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    kind = models.CharField(max_length=255, blank=True, null=True)


@reversion.register(follow=["rootobject_ptr"])
class Person(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    GENDER_CHOICES = (
        ("female", "female"),
        ("male", "male"),
        ("third gender", "third gender"),
    )
    first_name = models.CharField(max_length=255, help_text="The persons´s forename. In case of more then one name...", blank=True, null=True)
    profession = models.ManyToManyField(Profession, blank=True)
    professioncategory = models.ForeignKey(ProfessionCategory, on_delete=models.CASCADE, null=True)
    title = models.ManyToManyField(Title, blank=True)
    gender = models.CharField(max_length=15, choices=GENDER_CHOICES, blank=True, null=True)

    @property
    def oebl_kurzinfo(self):
        return self.texts.get(kind="ÖBL Kurzinfo")

    @property
    def oebl_haupttext(self):
        return self.texts.get(kind="ÖBL Haupttext")


@reversion.register(follow=["rootobject_ptr"])
class Place(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    kind = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True, verbose_name="latitude")
    lng = models.FloatField(blank=True, null=True, verbose_name="longitude")


@reversion.register(follow=["rootobject_ptr"])
class Work(LegacyStuffMixin, LegacyDateMixin, AbstractEntity):
    kind = models.CharField(max_length=255, blank=True, null=True)


@reversion.register
class Text(models.Model):
    TEXTTYPE_CHOICES = [
            (1, "Place description ÖBL"),
            (2, "ÖBL Haupttext"),
            (3, "ÖBL Kurzinfo"),
            (4, "Place review comments"),
            (5, "Commentary Staribacher"),
            (6, "Online Edition Haupttext"),
            (7, "Nachrecherche"),
            (8, "Soziale Herkunft"),
            (9, "Verwandtschaft"),
            (10, "Ausbildung / Studium / Studienreisen und diesbezügliche Ortsangaben"),
            (11, "Berufstätigkeit / Lebensstationen und geographische Lebensmittelpunkte"),
            (12, "Mitgliedschaften, Orden, Auszeichnungen und diesbezügliche Ortsangaben"),
            (13, "Literatur"),
            (14, "Beruf(e)"),
            (15, "Sterbedatum"),
            (16, "Adelsprädikat"),
            (17, "Übersiedlung, Emigration, Remigration"),
            (18, "Weitere Namensformen"),
            (19, "Geburtsdatum"),
            (20, "Sterbeort"),
            (21, "Geburtsort"),
            (22, "Religion(en)"),
            (23, "Name"),
            (24, "Übersiedlungen, Emigration, Remigration"),
            (25, "Pseudonyme"),
            (26, "Soziale Herkunft"),
            (27, "ÖBL Werkverzeichnis"),
    ]

    text = models.TextField(blank=True)
    kind = models.CharField(max_length=255, blank=True, null=True, choices=TEXTTYPE_CHOICES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
