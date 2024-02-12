from django.forms import CharField, Textarea
from apis_ontology.models import Person, Text
from crispy_forms.layout import Layout, HTML
from apis_core.generic.forms import GenericModelForm

TEXTTYPE_CHOICES_MAIN = ["ÖBL Haupttext", "ÖBL Werkverzeichnis"]


class LegacyStuffMixinForm(GenericModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        more_details = Layout(HTML("<details><summary>More details</summary>"))
        for ttypenr, ttype in Text.TEXTTYPE_CHOICES:
            self.fields[ttype] = CharField(required=False, widget=Textarea)
            if instance := kwargs.get("instance"):
                try:
                    text = instance.texts.get(kind=ttype)
                    self.fields[ttype].initial = text.text
                except Text.DoesNotExist:
                    pass
            if ttype not in TEXTTYPE_CHOICES_MAIN:
                more_details.append(ttype)
        more_details.extend(["notes", "status", "review", "published"])
        more_details.append(HTML("</details>"))

        all_other_fields = [f for f in self.fields if f not in more_details]
        self.helper.layout = Layout(*all_other_fields, more_details)

    def save(self, *args, **kwargs):
        obj = super().save(*args, **kwargs)
        for ttypenr, ttype in Text.TEXTTYPE_CHOICES:
            if self.cleaned_data[ttype]:
                text, created = obj.texts.get_or_create(kind=ttype)
                text.text = self.cleaned_data[ttype]
                text.save()
        return obj


class PersonForm(LegacyStuffMixinForm):
    field_order = ["first_name", "name", "start_date_written", "end_date_written", "gender", "profession", "title",]

    class Meta:
        model = Person
        fields = "__all__"
