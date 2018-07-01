import pandas as pd
import string

from mots.models import Mot
from mots.models import FlexionFéminine


Mot.objects.all().delete()

raw_data = pd.read_csv("../../raw-data/lexique.csv")
raw_data = raw_data[0:]
raw_data = raw_data.fillna("")

terminaisons = [
              {"terminaisons": ["teur"],  "nom": "teur"},  # 3.3
              {"terminaisons": ["eur"], "nom": "eur"},  # 3.2
              {"terminaisons": ["a", "o", "u"], "nom": "a,o,u"},  # 2.c
              {"terminaisons": ["i", "é"], "nom": "i,é"},  # 2.c
              {"terminaisons": ["e"], "nom": "e"},  # 2.b
           ]

voyels = ["a", "e", "i", "o", "u"]
consonnes = [l for l in string.ascii_lowercase if l not in voyels]
terminaisons.append({"terminaisons": consonnes, "nom": "consonne"})

# for idx, row in raw_data.iloc[1000:].iterrows():
for idx, row in raw_data.iterrows():
    print(idx)
    print(row["masculin"])

    # Mot au masc et singulier
    masculin_sings = str(row["masculin"]).split(",")
    masculin_plurs = str(row["masculin pluriel"]).split(",")

    masc_sing = masculin_sings[0]
    masc_plur = masculin_plurs[0]

    args = {"masculin_singulier": masc_sing,
            "masculin_pluriel": masc_plur}

    # Ajoute les autres formes du masculin dans une liste.
    args["masculin_sinuglier_autres"] = masculin_sings[1:]
    args["masculin_pluriel_autres"] = masculin_plurs[1:]

    # Source
    args["source"] = "import_spredsheet_01"
    # TODO: il faut indiqué les sources qui ont générer le mot (wiki, lefff, dicollecte).
    #       peut-être dans la section "commentaires internes"
    # args["dictionnaires"] = [s.replace("leff", "lefff").replace("wiki", "wiktionnaire") for s in row["sources"].split(",")]

    # Fréquence (default None, on va les ajouter plus tard)
    args["fréquence"] = {}

    # Notes
    commentaires = row["commentaires"].strip()

    commentaires_internes = []
    if commentaires != "":
        commentaires_internes.append(commentaires.strip())

    # Terminaisons
    for term in terminaisons:
        ending_match = False
        for ending in term["terminaisons"]:
            if masc_sing.endswith(ending):
                ending_match = True
        if ending_match:
            args["terminaison"] = term["nom"]
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

    # Ajouter des infos sur la création du mot dans les commentaires
    args["commentaires_internes"] = commentaires_internes

    # Créer le mot
    mot = Mot(**args)
    mot.save()

    # ===============
    # Créer les flexions
    # ===============
    # Ajoute seulement les flexions qui étaient validé à la main par nous
    # Les autres flexions seront ajoutés plus tard.
    if row["validation"].strip() != "":
        existing_flex_sing = []
        existing_flex_plur = []

        # Trouver les flexions dans les 4 colonnes
        for i in range(1, 4):

            # Trouver les flexions
            prefix = "{idx} féminin ".format(idx=i)
            singulier = row[prefix + "singulier"].lower().strip()
            pluriel = row[prefix + "pluriel"].lower().strip()

            # Ajouter les commentaires
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
            flex_freq = {}

            source = "import G-sheets"

            if singulier != "" and pluriel != "":
                flex_args = {
                    "mot_ref_id": mot.id,
                    "singulier": singulier,
                    "pluriel": pluriel,
                    "fréquence": flex_freq,
                    "validation": validation,
                    "commentaires_internes": commentaires_internes,
                    "source": source,
                }

                flex = FlexionFéminine(**flex_args)
                flex.save()
