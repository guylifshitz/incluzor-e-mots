from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

from django.http import HttpResponse
from .models import Mot
from .forms import MotForm
from .forms import FlexionFéminineFormSet, FéminineFormSetHelper
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.db import transaction
from django.urls import reverse_lazy

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from html5print import HTMLBeautifier

import json


def index(request):
    contact_list = Mot.objects.filter(masculin_singulier="abyssin").order_by('id')
    paginator = Paginator(contact_list, 100) # Show 25 contacts per page

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


def calculate_fréquence(form):
    fréquence_ngrams_singulier = form["fréquence_ngrams_singulier"].value()
    fréquence_ngrams_pluriel = form["fréquence_ngrams_pluriel"].value()

    fréquence_google_singulier = form["fréquence_google_singulier"].value()
    fréquence_google_pluriel = form["fréquence_google_pluriel"].value()

    fréquence = {
        "ngrams": {
            "singulier": fréquence_ngrams_singulier,
            "pluriel": fréquence_ngrams_pluriel,
        },
        "google": {
            "singulier": fréquence_google_singulier,
            "pluriel": fréquence_google_pluriel,
        }
    }

    return fréquence


class EditMot(UpdateView):
    model = Mot
    success_url = reverse_lazy('mots:index')
    form_class = MotForm

    def get_context_data(self, **kwargs):
        data = super(EditMot, self).get_context_data(**kwargs)

        data["word"] = self.object.masculin_singulier

        if self.request.POST:
            pass
            data['flexion_fem_members'] = FlexionFéminineFormSet(self.request.POST, instance=self.object, prefix="fem")
            data['fem_helper'] = FéminineFormSetHelper()
        else:
            data['flexion_fem_members'] = FlexionFéminineFormSet(instance=self.object, prefix="fem")
            data['fem_helper'] = FéminineFormSetHelper()

            for subform in data['flexion_fem_members'].forms:
                subform.initial = subform.initial

                subform.initial["fréquence_ngrams_singulier"] = get_json_val(subform.instance.fréquence, "ngrams", "singulier")
                subform.initial["fréquence_ngrams_pluriel"] = get_json_val(subform.instance.fréquence, "ngrams", "pluriel")
                subform.initial["fréquence_google_singulier"] = get_json_val(subform.instance.fréquence, "google", "singulier")
                subform.initial["fréquence_google_pluriel"] = get_json_val(subform.instance.fréquence, "google", "pluriel")

        return data

    def get_initial(self):
        initial = super(EditMot, self).get_initial()

        # Fréquence
        initial["fréquence_ngrams_singulier"] = self.object.fréquence["ngrams"]["singulier"]
        initial["fréquence_ngrams_pluriel"] = self.object.fréquence["ngrams"]["pluriel"]
        initial["fréquence_google_singulier"] = self.object.fréquence["google"]["singulier"]
        initial["fréquence_google_pluriel"] = self.object.fréquence["google"]["pluriel"]

        # Notes
        if self.object.notes_internes:
            initial["notes_internes_text"] = "\n\n".join(self.object.notes_internes)

        return initial

    def form_invalid(self, form):
        print("Form Invalid")
        print(form._errors)
        return super(EditMot, self).form_invalid(form)

    def form_valid(self, form):
        context = self.get_context_data()

        new_note_interne = form["new_note_interne"].value()

        with transaction.atomic():
            self.object = form.save(commit=False)

            # Append to notes internes list
            if self.object.notes_internes and new_note_interne.strip() != "":
                self.object.notes_internes.append(new_note_interne)
            else:
                self.object.notes_internes = [new_note_interne]

            self.object.fréquence = calculate_fréquence(form)
            self.object.save()

            # Flexion Formset
            flexion_fem_members = context["flexion_fem_members"]

            if flexion_fem_members.is_valid():
                flexion_fem_members.instance = self.object

                for flexi_form in flexion_fem_members:
                    flexi_obj = flexi_form.save(commit=False)

                    # Fréquence : Créer le JSON
                    flexi_obj.fréquence = calculate_fréquence(flexi_form)
                    flexi_obj.save()
            else:
                print("Flexion invalid: ")
                print(flexion_fem_members.errors)
                return self.form_invalid(form)

        return super(EditMot, self).form_valid(form)
