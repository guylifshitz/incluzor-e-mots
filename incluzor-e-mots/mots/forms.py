from django.forms import ModelForm, Form
from django.forms import inlineformset_factory, formset_factory
from .models import Mot, Flexion, FlexionFéminine

from django.forms import Textarea
from django.forms import CharField
from django.forms import DateField,ChoiceField
from django.forms import IntegerField
from django.forms import SelectDateWidget
from django.forms import MultipleChoiceField
from django.forms import CheckboxSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from django.contrib.postgres.fields import JSONField, ArrayField

from django import forms
from crispy_forms.layout import Submit

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Button, Fieldset, HTML, Button, Field
from crispy_forms.bootstrap import StrictButton, InlineField, FormActions, FieldWithButtons, Accordion, AccordionGroup, UneditableField, InlineCheckboxes


def correct_arraylist(self):
    # Correct required for ArrayList (seems to be a mistake with Crispy forms?)
    for field in self._meta.model._meta.get_fields():
        if field.name not in self._meta.exclude:
            if field.get_internal_type() == "ArrayField":
                self.fields[field.name].required = not(field.null)


class Row(Div):
    css_class="row"


dictionnairesLayout = Layout(
    Row(
        Div(
            Row(HTML("<strong>Dictionnaires </strong>"), css_class="card-header"),
            Div(
                Row(
                    Div(FieldWithButtons('dict_larousse', StrictButton('Show', css_class="btn-outline-secondary toggle-dict"), StrictButton('Get', css_class="btn-outline-secondary get-dict")), css_class="col-sm-3"),
                    Div(FieldWithButtons('dict_cnrtl', StrictButton('Show', css_class="btn-outline-secondary toggle-dict"), StrictButton('Get', css_class="btn-outline-secondary get-dict")), css_class="col-sm-3"),
                    Div(FieldWithButtons('dict_wiktionnaire', StrictButton('Show', css_class="btn-outline-secondary toggle-dict"), StrictButton('Get', css_class="btn-outline-secondary get-dict")), css_class="col-sm-3"),
                    Div(FieldWithButtons('dict_littré', StrictButton('Show', css_class="btn-outline toggle-dict"), StrictButton('Get', css_class="btn-outline-secondary get-dict")), css_class="col-sm-3"),
                ),
                Row(
                    Button("Toogle", "toggle", css_class="toggle-iframe btn-outline-secondary col-sm-3"),
                ),
                Row(
                    HTML("<iframe class='dict-iframe' src='about:blank'></iframe>"),
                ),
            ),
            # css_class="card card-with-padding col-sm-12",
            css_class="card card-with-padding",
        ),
        css_class="col-sm-12",
    )
    # Div(
    #     Row(
    #         Div(FieldWithButtons('dict_reverso', StrictButton('Show', css_class="btn-outline-secondary toggle-dict"), StrictButton('Get', css_class="btn-outline-secondary get-dict")), css_class="col-sm-3"),
    #     ),
    #     css_class="col-sm-12",
    # ),

)

fréquenceLayout = Layout(
    Row(
        Div(
            Div(
                Div(HTML("<strong>Féquence : Ngrams </strong>"), css_class="card-header"),
                Div(
                    Div(FieldWithButtons('fréquence_ngrams_singulier', StrictButton('Get', css_class="btn-outline-secondary freq-button")), css_class=""),
                    Div(FieldWithButtons('fréquence_ngrams_pluriel', StrictButton('Get', css_class="btn-outline-secondary freq-button")), css_class=""),
                ),
                css_class="card card-with-padding-only"
            ),
            css_class='col-sm-6'
        ),
    ),
)

notesLayout = Layout(
    Row(
        Div(
            Row(HTML("<strong>Notes </strong>"), css_class="card-header"),
            Div(
                Div(
                    Div('commentaire_externe', css_class="col-sm-6"),
                    Div('liens', css_class="col-sm-6"),
                    css_class='row'
                ),
                Div(
                    Div(Field('commentaires_internes_text', readonly=True), css_class="col-sm-6"),
                    Div('new_commentaire_interne', css_class="col-sm-6"),
                    css_class='row'
                ),
            ),
            # css_class="card card-with-padding col-sm-12",
            css_class="card card-with-padding",
        ),
        css_class="col-sm-12",
    )
)


DICTIONNAIRES_STATES = (
    ("à traiter", "À traiter"),
    ("existe", "Existe"),
    ("non-existant", "Non-existant"),
)


class GeneralForm(ModelForm):

    # Commentaires
    new_commentaire_interne = CharField(
        max_length=2000,
        widget=Textarea(),
        help_text='Ajouter une commentaire.',
        required=False,
    )

    commentaires_internes_text = CharField(
        max_length=2000,
        widget=Textarea(),
        required=False,
    )

    dict_larousse = ChoiceField(
        required=False,
        choices=DICTIONNAIRES_STATES,
        label="Larousse",
    )

    dict_cnrtl = ChoiceField(
        required=False,
        choices=DICTIONNAIRES_STATES,
        label="CNRTL",
    )

    dict_reverso = ChoiceField(
        required=False,
        choices=DICTIONNAIRES_STATES,
        label="Reverso",
    )

    dict_littré = ChoiceField(
        required=False,
        choices=DICTIONNAIRES_STATES,
        label="Littré",
    )

    dict_wiktionnaire = ChoiceField(
        required=False,
        choices=DICTIONNAIRES_STATES,
        label="Wiktionnaire",
    )

    # Fréquence
    fréquence_ngrams_singulier = IntegerField(label="Singulier")
    fréquence_ngrams_pluriel = IntegerField(label="Pluriel")


class MotForm(GeneralForm):

    def __init__(self, *args, submit_title="TITLE", **kwargs):
        super(MotForm, self).__init__(*args, **kwargs)

        correct_arraylist(self)

        # Crérer le helper (pour le rendering)
        self.helper = FormHelper(self)

        self.helper.form_tag = False
        self.helper.render_required_fields = True

        self.helper.form_class = 'form-vertical'
        self.helper.form_id = 'id-mot-form'
        self.helper.layout = Layout(
            Div(
                Div(HTML("<h3>Masculins</h3>"), css_class=("card-header")),
                Div(
                    Row(
                        Div('masculin_singulier', css_class="col-sm-3"),
                        Div('masculin_pluriel', css_class="col-sm-3"),
                        Div('validation', css_class="col-sm-2"),
                        Div('terminaison', css_class="col-sm-2"),
                        UneditableField('source', readonly=True),
                    ),
                    Row(
                        InlineCheckboxes('problème_signalé', css_class="col-sm-4"),
                        Field('visible', css_class="col-sm-4"),
                    ),
                    Row(
                        Div('masculin_sinuglier_autres', css_class="col-sm-6"),
                        Div('masculin_pluriel_autres', css_class="col-sm-6"),
                        css_class='row'
                    ),
                    fréquenceLayout,
                    dictionnairesLayout,
                    notesLayout,
                    css_class="card-body"
                ),
                css_class="card"
            ),
            # Div(
            #     Div(HTML("<h3>Caracteristiques</h3>"), css_class=("card-header")),
            #     Div(
            #         Div(
            #             # HTML('source: {{ form.instance.source }}'),
            #             css_class='row'
            #         ),
            #         Div(
            #             Div('commentaire_externe', css_class="col-sm-6"),
            #             Div('liens', css_class="col-sm-6"),
            #             css_class='row'
            #         ),
            #         Div(
            #             Div(Field('commentaires_internes_text', readonly=True), css_class="col-sm-6"),
            #             Div('new_commentaire_interne', css_class="col-sm-6"),
            #             css_class='row'
            #         ),
            #         css_class="card-body"
            #     ),
            #     css_class="card"
            # ),
        )

    # def clean(self):
        # super().clean()

    class Meta:
        model = Mot
        exclude = ("fréquence", "commentaires_internes", "dictionnaires")
        help_texts = {
            'liens': "Un URL par ligne.",
        }
        widgets = {
            'liens': forms.Textarea(),
        }


class FlexionForm(GeneralForm):

    def __init__(self, *args, **kwargs):
        super(FlexionForm, self).__init__(*args, **kwargs)

        correct_arraylist(self)

        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.render_required_fields = True

    class Meta:
        model = Flexion
        exclude = ("fréquence", "commentaires_internes", "dictionnaires")


class FlexionFéminineForm(FlexionForm):
    class Meta:
        model = FlexionFéminine
        exclude = ("fréquence", "commentaires_internes", "dictionnaires")
        widgets = {
            'liens': forms.Textarea(),
        }
        help_texts = {
            'liens': "Un URL par ligne.",
        }


class FéminineFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FéminineFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.render_required_fields = True
        self.form_tag = False

        self.layout = Layout(
            Div(
                Div(HTML("<h3>Féminins : {{ subform.singulier.value  }}</h3>"), css_class=("card-header")),
                Div(
                    Row(
                        Field('singulier', wrapper_class="col-sm-3"),
                        Field('pluriel', wrapper_class="col-sm-3"),
                        Field('validation', wrapper_class="col-sm-2"),
                        Field('stratégie', wrapper_class="col-sm-2"),
                        Field('libelles', wrapper_class="col-sm-2"),
                    ),
                    fréquenceLayout,
                    dictionnairesLayout,
                    notesLayout,
                    css_class="card-body"
                ),
                Field('DELETE'),
                css_class="card flexion_entry"
            ),
        )
