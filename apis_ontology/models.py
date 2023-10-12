from datetime import datetime, timezone
from apis_core.apis_relations.models import TempTriple
from django.dispatch import receiver
import reversion
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from apis_core.apis_entities.models import AbstractEntity
from apis_core.apis_relations.models import Triple
from apis_core.core.models import LegacyDateMixin
from apis_core.utils import DateParser
from simple_history.models import HistoricalRecords
from simple_history.signals import (
    pre_create_historical_record,
    pre_create_historical_m2m_records,
)


class LegacyStuffMixin(models.Model):
    review = review = models.BooleanField(
        default=False,
        help_text="Should be set to True, if the data record holds up quality standards.",
    )
    status = models.CharField(max_length=100, blank=True)
    references = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    published = models.BooleanField(default=False)

    texts = GenericRelation("Text")

    class Meta:
        abstract = True


class APISHistoryTableBase(models.Model):
    class Meta:
        abstract = True

    def get_triples_for_version(self):
        triples = TempTriple.history.as_of(self.history_date).filter(
            Q(subj=self.instance) | Q(obj=self.instance)
        )
        return triples


class VersionMixin(models.Model):
    history = HistoricalRecords(inherit=True, bases=[APISHistoryTableBase])
    __history_date = datetime.now()

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    class Meta:
        abstract = True


class Source(VersionMixin):
    orig_filename = models.CharField(max_length=255, blank=True)
    indexed = models.BooleanField(default=False)
    pubinfo = models.CharField(max_length=400, blank=True)
    author = models.CharField(max_length=255, blank=True)
    orig_id = models.PositiveIntegerField(blank=True, null=True)

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self):
        if self.author and self.orig_filename:
            return f"{self.orig_filename}, stored by {self.author}"
        return f"(ID: {self.id})".format(self.id)


class Title(VersionMixin):
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Profession(VersionMixin):
    name = models.CharField(max_length=255, blank=True)
    parent = models.ForeignKey("self", blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Event(LegacyStuffMixin, LegacyDateMixin, AbstractEntity, VersionMixin):
    kind = models.CharField(max_length=255, blank=True, null=True)


class Institution(LegacyStuffMixin, LegacyDateMixin, AbstractEntity, VersionMixin):
    kind = models.CharField(max_length=255, blank=True, null=True)


class Place(LegacyStuffMixin, LegacyDateMixin, AbstractEntity, VersionMixin):
    kind = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True, verbose_name="latitude")
    lng = models.FloatField(blank=True, null=True, verbose_name="longitude")


class Person(LegacyStuffMixin, LegacyDateMixin, AbstractEntity, VersionMixin):
    GENDER_CHOICES = (
        ("female", "female"),
        ("male", "male"),
        ("third gender", "third gender"),
    )
    first_name = models.CharField(
        max_length=255,
        help_text="The persons´s forename. In case of more then one name...",
        blank=True,
        null=True,
    )
    profession = models.ManyToManyField(Profession, blank=True)
    title = models.ManyToManyField(Title, blank=True)
    gender = models.CharField(
        max_length=15, choices=GENDER_CHOICES, blank=True, null=True
    )


class Work(LegacyStuffMixin, LegacyDateMixin, AbstractEntity, VersionMixin):
    kind = models.CharField(max_length=255, blank=True, null=True)


class Text(VersionMixin):
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
    kind = models.CharField(
        max_length=255, blank=True, null=True, choices=TEXTTYPE_CHOICES
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey("content_type", "object_id")
