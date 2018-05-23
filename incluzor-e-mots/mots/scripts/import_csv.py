# open file & create csvreader
import pandas as pd

# import the relevant model
from mots.models import Mot
from mots.models import FlexionFéminine

import string
import mots.utils as utils

Mot.objects.all().delete()

raw_data = pd.read_csv("../../raw-data/lexique.csv")
raw_data = raw_data[0:]
raw_data = raw_data.fillna("")
# raw_data["masculin"] = raw_data["masculin"].fillna("")
# raw_data["masculin pluriel"] = raw_data["masculin pluriel"].fillna("")
# raw_data["commentaires"] = raw_data["commentaires"].fillna("")


def safe_get(data, keys):

    value = data

    if type(keys) == list:
        for key in keys:
            try:
                value = value[key]
            except:
                return None
    else:
        try:
            value = value[keys]
        except:
            return None

    return value


# for idx, row in raw_data.iloc[1000:].iterrows():
for idx, row in raw_data.iterrows():
    # add some custom validation\parsing for some of the fields

    print(idx)
    print(row["masculin"])

    masculin_sings = str(row["masculin"]).split(",")
    masculin_plurs = str(row["masculin pluriel"]).split(",")

    masc_sing = masculin_sings[0]
    masc_plur = masculin_plurs[0]

    args = {"masculin_singulier": masc_sing,
            "masculin_pluriel": masc_plur}

    args["masculin_sinuglier_autres"] = masculin_sings[1:]
    args["masculin_pluriel_autres"] = masculin_plurs[1:]

    args["source"] = "import_spredsheet_01"

    # args["dictionnaires"] = [s.replace("leff", "lefff").replace("wiki", "wiktionnaire") for s in row["sources"].split(",")]

    # Fréquence (default none)
    # ngrams_ms = safe_get(utils.get_fréquence(masc_sing), "ngrams")
    # ngrams_mp = safe_get(utils.get_fréquence(masc_plur), "ngrams")
    # args["fréquence"] = {"ngrams":{"singulier":ngrams_ms, "pluriel":ngrams_mp}}
    args["fréquence"] = {}

    # Notes
    commentaires = row["commentaires"].strip()

    commentaires_internes = []
    if commentaires != "":
        commentaires_internes.append(commentaires.strip())

    # Terminaisons
    endings = [
                  {"endings": ["teur"],  "name": "teur"},  # 3.3
                  {"endings": ["eur"], "name": "eur"},  # 3.2
                  {"endings": ["a", "o", "u"], "name": "a,o,u"},  # 2.c
                  {"endings": ["i", "é"], "name": "i,é"},  # 2.c
                  {"endings": ["e"], "name": "e"},  # 2.b
               ]

    consonants = list(string.ascii_lowercase)
    consonants.remove("a"); consonants.remove("e"); consonants.remove("i"); consonants.remove("o"); consonants.remove("u")
    endings.append({"endings": consonants, "name": "consonne"})

    for ending_category in endings:
        ending_match = False
        for ending in ending_category["endings"]:
            if masc_sing.endswith(ending):
                ending_match = True
        if ending_match:
            args["terminaison"] = ending_category["name"]
            break

    # Validation
    flexion_created = False
    for i in range(1, 4):
        prefix = "{idx} féminin ".format(idx=i)
        if row[prefix + "singulier"].strip() != "" or row[prefix + "pluriel"].strip() != "":
            flexion_created = True

    if row["validation"].lower().startswith("v"):
        validation = "valide"
    elif row["validation"].lower().startswith(("d", "f")):
        validation = "doute"
        commentaires_internes.append("Validation: " + row["validation"])
    else:
        validation = "à traiter"
    args["validation"] = validation

    args["commentaires_internes"] = commentaires_internes
    mot = Mot(**args)
    mot.save()

    if row["validation"].strip() != "":
        # Create flexions feminines
        existing_flex_sing = []
        existing_flex_plur = []
        for i in range(1, 4):
            prefix = "{idx} féminin ".format(idx=i)
            singulier = row[prefix + "singulier"].lower().strip()
            pluriel = row[prefix + "pluriel"].lower().strip()

            commentaires_internes = []

            # Ajoute les commentaires dans toutes les flexions aussi pour
            # le donner plus de visibilité
            if commentaires != "":
                commentaires_internes.append(commentaires.strip())

            # Indiquer des doublons
            if singulier in existing_flex_sing or pluriel in existing_flex_plur:
                validation = "doute"
                commentaires_internes.append("Doublon de la flexion " + singulier)

            existing_flex_sing.append(singulier)
            existing_flex_plur.append(pluriel)

            # Fréquence (default none)
            # ngrams_ms = safe_get(utils.get_fréquence(singulier), "ngrams")
            # ngrams_mp = safe_get(utils.get_fréquence(pluriel), "ngrams")
            # flex_freq = {"ngrams":{"singulier":ngrams_ms, "pluriel":ngrams_mp}}
            flex_freq = {}

            flex_args = {}
            if singulier != "" and pluriel != "":
                flex_args = {
                    "mot_ref_id": mot.id,
                    "singulier": singulier,
                    "pluriel": pluriel,
                    "fréquence": flex_freq,
                    "validation": validation,
                    "commentaires_internes": commentaires_internes,
                }

                flex = FlexionFéminine(**flex_args)
                flex.save()
