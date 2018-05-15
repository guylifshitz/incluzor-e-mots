from django.forms import ModelForm, Form
from django.forms import inlineformset_factory, formset_factory
from .models import Mot, Flexion, FlexionMasculine, FlexionFéminine

from django.forms import Textarea
from django.forms import CharField
from django.forms import DateField
from django.forms import IntegerField
from django.forms import SelectDateWidget
from django.forms import MultipleChoiceField
from django.forms import CheckboxSelectMultiple
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout

from django import forms
from crispy_forms.layout import Submit

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Button, Fieldset, HTML, Button, Field
from crispy_forms.bootstrap import StrictButton, InlineField, FormActions, FieldWithButtons, Accordion, AccordionGroup


class MotForm(ModelForm):

    # Notes
    new_note_interne = CharField(
        max_length=2000,
        widget=Textarea(),
        help_text='Ajouter une note.',
        required=False,
    )

    notes_internes_text = CharField(
        max_length=2000,
        widget=Textarea(),
        required=False,
    )

    # Fréquence
    fréquence_google_singulier = IntegerField(label="Singulier")
    fréquence_google_pluriel = IntegerField(label="Pluriel")

    fréquence_ngrams_singulier = IntegerField(label="Singulier")
    fréquence_ngrams_pluriel = IntegerField(label="Pluriel")

    def __init__(self, *args, submit_title="TITLE", **kwargs):
        super(MotForm, self).__init__(*args, **kwargs)

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
                    Div(
                        Div('masculin_singulier', css_class="col-sm-6"),
                        Div('masculin_pluriel', css_class="col-sm-6"),
                        css_class='row'
                    ),
                    Div(
                        Div(
                            Div(
                                Div(HTML("<strong>Féquence : Google</strong>"), css_class="card-header"),
                                Div(FieldWithButtons('fréquence_google_singulier', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                Div(FieldWithButtons('fréquence_google_pluriel', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                css_class="card card-with-padding"
                            ),
                            css_class='col-sm-6'
                        ),
                        Div(
                            Div(
                                Div(HTML("<strong>Féquence : Ngrams </strong>"), css_class="card-header"),
                                Div(FieldWithButtons('fréquence_ngrams_singulier', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                Div(FieldWithButtons('fréquence_ngrams_pluriel', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                css_class="card card-with-padding"
                            ),
                            css_class='col-sm-6'
                        ),
                        css_class='row'
                    ),
                    Div(
                        Accordion(
                            AccordionGroup('Autre flexions masculine',
                                           )
                        )
                    ),
                    css_class="card-body"
                ),
                css_class="card"
            ),
            Div(
                Div(HTML("<h3>Characteristiques</h3>"), css_class=("card-header")),
                Div(
                    Div(
                        Div('terminaison', css_class="col-sm-6"),
                        css_class='row'
                    ),
                    Div(
                        Div('note_externe', css_class="col-sm-12"),
                        css_class='row'
                    ),
                    Div(
                        Div('new_note_interne', css_class="col-sm-6"),
                        Div(Field('notes_internes_text', readonly=True), css_class="col-sm-6"),
                        css_class='row'
                    ),
                    Div(
                        Div('validation', css_class="col-sm-6"),
                        css_class='row'
                    ),
                    css_class="card-body"
                ),
                css_class="card"
            ),
        )
        self.helper.layout.append(Submit('save', 'Save'))

    def clean(self):
        super().clean()
        print("CLEAN")

    class Meta:
        model = Mot
        exclude = ("fréquence", "notes_internes")
        help_texts = {
            # 'masculin_singulier': "TEDST",
        }
        widgets = {
            # 'notes_internes': forms.Textarea(attrs={'placeholder': u'Liste des notes créer'}),
        }


class FlexionForm(ModelForm):

    # Fréquence (converti du JSON)
    fréquence_google_singulier = IntegerField(label="Singulier")
    fréquence_google_pluriel = IntegerField(label="Pluriel")

    fréquence_ngrams_singulier = IntegerField(label="Singulier")
    fréquence_ngrams_pluriel = IntegerField(label="Pluriel")

    # Note (nouvelle note à ajouter à la liste des notes)

    new_note_interne = CharField(
        max_length=2000,
        widget=Textarea(),
        help_text='Ajouter une note.',
        required=False,
    )

    DICTIONNAIRES = (
        ('larousse', 'Larousse'),
        ("rober", 'Robert'),
        ("wiktionnaire", 'Wiktionnaire'),
        ("dicollecte", 'Dicollecte'),
    )
    VALIDATION_STATE = (
        ('générer', 'Générer'),
        ("à-valider", 'À valider'),
        ("erreur", 'Erreur signalé'),
        ("non-valide", 'Non-valide'),
        ("valide", 'Valide'),
    )

    dictionnaires = MultipleChoiceField(
        required=False,
        widget=CheckboxSelectMultiple(attrs={'class': 'form-check'}),
        choices=DICTIONNAIRES,
    )

    def __init__(self, *args, **kwargs):
        super(FlexionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-inline'
        self.helper.render_required_fields = True

    class Meta:
        model = Flexion
        exclude = ("liens", "fréquence", "notes_internes")


class FlexionMasculineForm(FlexionForm):
    class Meta:
        model = FlexionMasculine
        exclude = ()


class FlexionFéminineForm(FlexionForm):
    class Meta:
        model = FlexionFéminine
        exclude = ("liens","fréquence","notes_internes")
        widgets = {
            # 'notes_internes': forms.Textarea(attrs={'placeholder': u'Liste des notes créer'}),
        }


class Row(Div):
    css_class = "form-row"


class FéminineFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(FéminineFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.render_required_fields = True
        self.form_tag = False

        # self.render_unmentioned_fields = True
        # self.template = 'bootstrap/table_inline_formset.html'

        self.layout = Layout(
            Div(
                Div(HTML("<h3>Féminins</h3>"), css_class=("card-header")),
                Div(
                    Row(
                        Field('singulier', wrapper_class="col-sm-2"),
                        Field('pluriel', wrapper_class="col-sm-2"),
                        Field('dictionnaires', wrapper_class="col-sm-2"),
                        Field('tags', wrapper_class="col-sm-2"),
                        Field('validation', wrapper_class="col-sm-2"),
                        Field('libelles', wrapper_class="col-sm-2"),
                    ),
                    Div(
                        Div(
                            Div(
                                Div(HTML("<strong>Féquence : Google</strong>"), css_class="card-header"),
                                Div(FieldWithButtons('fréquence_google_singulier', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                Div(FieldWithButtons('fréquence_google_pluriel', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                css_class="card card-with-padding-only"
                            ),
                            css_class='col-sm-3'
                        ),
                        Div(
                            Div(
                                Div(HTML("<strong>Féquence : Ngrams </strong>"), css_class="card-header"),
                                Div(FieldWithButtons('fréquence_ngrams_singulier', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                Div(FieldWithButtons('fréquence_ngrams_pluriel', StrictButton('Get', css_class="btn-outline-secondary")), css_class=""),
                                css_class="card card-with-padding-only"
                            ),
                            css_class='col-sm-3'
                        ),
                        css_class='row'
                    ),
                    Accordion(
                        AccordionGroup(
                            "Notes",
                            Div(
                                Div(
                                    Div('note_externe', css_class="col-sm-12"),
                                    css_class='row'
                                ),
                                Div(
                                    Div('new_note_interne', css_class="col-sm-6"),
                                    Div(Field('notes_internes', readonly=True), css_class="col-sm-6"),
                                    css_class='row'
                                ),
                            ),
                        ),
                    ),
                    css_class="card-body"
                ),
                Field('DELETE'),
                css_class="card flexion_entry"
            ),
        )

# FlexionMasculineFormSet = inlineformset_factory(Mot, FlexionMasculine, form=FlexionMasculineForm, extra=1)
FlexionFéminineFormSet = inlineformset_factory(Mot, FlexionFéminine, form=FlexionFéminineForm, extra=1, can_delete=True)
