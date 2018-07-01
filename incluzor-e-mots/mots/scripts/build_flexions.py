# open file & create csvreader
import pandas as pd
# import the relevant model
from mots.models import Mot
from mots.models import FlexionFéminine
import string


mots = Mot.objects.all()

for mot in mots:
    masc_sing = mot.masculin_singulier
    masc_plur = mot.masculin_pluriel
    terminaison = mot.terminaison

    # TODO: add info about which rule was used to generate each flex
    fems = []

    if terminaison == "e":
        fems = [{"s": masc_sing, "p": masc_plur}]
    elif terminaison == "teur":
        fems = [
            {"s": masc_sing[:-4]+"trice", "p": masc_sing[:-4]+"trices"},
            {"s": masc_sing[:-3]+"esse", "p": masc_sing[:-3]+"esses"},
            {"s": masc_sing[:-3]+"oresse", "p": masc_sing[:-3]+"oresses"},
            {"s": masc_sing+"e", "p": masc_sing+"e"}
        ]
    elif terminaison == "eur":
        fems = [
                {"s": masc_sing[:-1]+"se", "p": masc_sing[:-1]+"ses"},
                {"s": masc_sing[:-2]+"sse", "p": masc_sing[:-2]+"sses"},
                {"s": masc_sing+"e", "p": masc_sing+"es"},
        ]

    print(masc_sing)
    if fems:
        [print(f["s"] + " | " + f["p"]) for f in fems]
    else:
        print("NONE")

    fem_existants = FlexionFéminine.objects.filter(mot_ref__pk=mot.pk).all()
    fem_existants_s = [fe.singulier for fe in fem_existants]
    print(fem_existants_s)

    for flexion in fems:
        if flexion["s"] not in fem_existants_s:
            singulier = flexion["s"]
            pluriel = flexion["p"]
            fréquence = {}
            validation = "à traiter"
            commentaires_internes = []
            source = "stratégie auto"

            flex_args = {
                "mot_ref_id": mot.pk,
                "singulier": singulier,
                "pluriel": pluriel,
                "fréquence": fréquence,
                "validation": validation,
                "commentaires_internes": commentaires_internes,
                "source": source
            }

            flex = FlexionFéminine(**flex_args)
            print("Added: " + flexion["s"])
            flex.save()

    print("-")

# if singulier in existing_flex_sing or pluriel in existing_flex_plur:
# validation = "doute"
# notes_internes.append("Doublon du flexion " + singulier)

# existing_flex_sing.append(singulier)
# existing_flex_plur.append(pluriel)

# # Fréquence (default none)
# ngrams_ms = safe_get(utils.get_fréquence(singulier), "ngrams")
# ngrams_mp = safe_get(utils.get_fréquence(pluriel), "ngrams")
# flex_freq = {"ngrams":{"singulier":ngrams_ms, "pluriel":ngrams_mp}, "google":{"singulier":None, "pluriel":None}}

# flex_args = {}
# if singulier != "" and pluriel != "":
# flex_args = {
#     "mot_id": mot.id,
#     "singulier": singulier,
#     "pluriel": pluriel,
#     "fréquence": flex_freq,
#     "validation": validation,
#     "notes_internes": notes_internes,
# }

# flex = FlexionFéminine(**flex_args)
# flex.save()

