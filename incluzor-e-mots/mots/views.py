from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from .models import Mot, FlexionFéminine
from .forms import MotForm
from .forms import FlexionFéminineForm, FéminineFormSetHelper
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.db import transaction
from django.urls import reverse_lazy
from django.forms import inlineformset_factory

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from html5print import HTMLBeautifier

import json
from django.db.models.expressions import RawSQL


def index(request):
    # contact_list = Mot.objects.filter().order_by('id')
    # contact_list = Mot.objects.all().order_by(RawSQL("fréquence->'ngrams'->'singulier'", ())).reverse()
    contact_list = Mot.objects.all().order_by("terminaison", "-id").reverse()

    paginator = Paginator(contact_list, 100)  # Show 25 contacts per page

    page = request.GET.get('page')
    mots = paginator.get_page(page)

    return render(request, 'mots/list.html', {'mots': mots})


def get_json_val(field, *args):
    res = field
    for arg in args:
        try:
            res = res[arg]
        except:
            return None
    return res


def build_fréquence_json(form):
    fréquence_ngrams_singulier = form["fréquence_ngrams_singulier"].value()
    fréquence_ngrams_pluriel = form["fréquence_ngrams_pluriel"].value()

    fréquence = {
        "ngrams": {
            "singulier": fréquence_ngrams_singulier,
            "pluriel": fréquence_ngrams_pluriel,
        },
    }

    return fréquence


def build_dictionnaires_json(form):
    dictionnaires = {
        "larousse": form["dict_larousse"].value(),
        "cnrtl": form["dict_cnrtl"].value(),
        "reverso": form["dict_reverso"].value(),
        "littré": form["dict_littré"].value(),
        "wiktionnaire": form["dict_wiktionnaire"].value(),
    }

    return dictionnaires


class EditMot(UpdateView):
    model = Mot
    success_url = reverse_lazy('mots:index')
    form_class = MotForm

    def get_context_data(self, **kwargs):
        data = super(EditMot, self).get_context_data(**kwargs)

        data["word"] = self.object.masculin_singulier

        FlexionFéminineFormSet = inlineformset_factory(Mot, FlexionFéminine, form=FlexionFéminineForm, extra=0, can_delete=True)

        if self.request.POST:
            pass
            data['flexion_fem_members'] = FlexionFéminineFormSet(self.request.POST, instance=self.object, prefix="fem")
            data['fem_helper'] = FéminineFormSetHelper()
        else:
            data['flexion_fem_members'] = FlexionFéminineFormSet(instance=self.object, prefix="fem")
            data['fem_helper'] = FéminineFormSetHelper()

            for subform in data['flexion_fem_members'].forms:
                subform.initial = subform.initial

                if subform.instance.fréquence:
                    subform.initial["fréquence_ngrams_singulier"] = get_json_val(subform.instance.fréquence, "ngrams", "singulier")
                    subform.initial["fréquence_ngrams_pluriel"] = get_json_val(subform.instance.fréquence, "ngrams", "pluriel")

                if subform.instance.liens:
                    subform.initial["liens"] = "\n".join(subform.instance.liens)

                if subform.instance.commentaires_internes:
                    subform.initial["commentaires_internes_text"] = "\n--------\n".join(subform.instance.commentaires_internes)

                if subform.instance.dictionnaires:
                    subform.initial["dict_larousse"] = get_json_val(subform.instance.dictionnaires, "larousse")
                    subform.initial["dict_cnrtl"] = get_json_val(subform.instance.dictionnaires, "cnrtl")
                    subform.initial["dict_reverso"] = get_json_val(subform.instance.dictionnaires, "reverso")
                    subform.initial["dict_littré"] = get_json_val(subform.instance.dictionnaires, "littré")
                    subform.initial["dict_wiktionnaire"] = get_json_val(subform.instance.dictionnaires, "wiktionnaire")

        return data

    def get_initial(self):
        initial = super(EditMot, self).get_initial()

        # Fréquence
        if self.object.fréquence:
            initial["fréquence_ngrams_singulier"] = get_json_val(self.object.fréquence, "ngrams", "singulier")
            initial["fréquence_ngrams_pluriel"] = get_json_val(self.object.fréquence, "ngrams", "pluriel")

        # Dictionnaires
        if self.object.dictionnaires:
            initial["dict_larousse"] = get_json_val(self.object.dictionnaires, "larousse")
            initial["dict_cnrtl"] = get_json_val(self.object.dictionnaires, "cnrtl")
            initial["dict_reverso"] = get_json_val(self.object.dictionnaires, "reverso")
            initial["dict_littré"] = get_json_val(self.object.dictionnaires, "littré")
            initial["dict_wiktionnaire"] = get_json_val(self.object.dictionnaires, "wiktionnaire")

        # Liens
        if self.object.liens:
            initial["liens"] = "\n".join(self.object.liens)

        # Commentaires
        if self.object.commentaires_internes:
            initial["commentaires_internes_text"] = "\n--------\n".join(self.object.commentaires_internes)

        return initial

    def form_invalid(self, form):
        print("Form Invalid")
        print(form._errors)
        return super(EditMot, self).form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()

        new_commentaire_interne = form["new_commentaire_interne"].value()

        with transaction.atomic():
            self.object = form.save(commit=False)

            # Append to commentaires internes list
            if self.object.commentaires_internes and new_commentaire_interne.strip() != "":
                self.object.commentaires_internes.append(new_commentaire_interne)
            else:
                self.object.commentaires_internes = [new_commentaire_interne]

            # Sauvgarde les JSONs
            self.object.dictionnaires = build_dictionnaires_json(form)
            self.object.fréquence = build_fréquence_json(form)
            self.object.liens = [lien.strip() for lien in form["liens"].value().split("\n")]

            self.object.save()

            # Sauvgarde le flexion formset
            flexion_fem_members = context["flexion_fem_members"]

            if flexion_fem_members.is_valid():
                flexion_fem_members.instance = self.object
                for flexi_form in flexion_fem_members:
                    flexi_obj = flexi_form.save(commit=False)

                    # Sauvgarde les JSONs
                    flexi_obj.fréquence = build_fréquence_json(flexi_form)
                    flexi_obj.dictionnaires = build_dictionnaires_json(flexi_form)

                    # Sauvgarde les liens (par ligne)
                    flexi_obj.liens = [lien.strip() for lien in flexi_form["liens"].value().split("\n")]

                    # Append to commentaires internes list
                    flexi_new_commentaire_interne = flexi_form["new_commentaire_interne"].value()
                    if flexi_obj.commentaires_internes and flexi_new_commentaire_interne.strip() != "":
                        flexi_obj.commentaires_internes.append(flexi_new_commentaire_interne)
                    else:
                        flexi_obj.commentaires_internes = [flexi_new_commentaire_interne]

                    # Commit
                    flexi_obj.save()
            else:
                print("Flexion invalid: ")
                print(flexion_fem_members.errors)
                return self.form_invalid(form)

        return super(EditMot, self).form_valid(form)
