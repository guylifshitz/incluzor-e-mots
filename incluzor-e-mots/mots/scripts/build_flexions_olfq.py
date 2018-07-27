import pandas as pd
from sqlalchemy import create_engine

# import the relevant model
from mots.models import Mot
from mots.models import FlexionFéminine

mots = Mot.objects.all()

engine = create_engine('postgresql://incluzor:PAN7kZBAGqXQd5FnQs37TtyKqNYKDhCbenRKA@api.incluzor.fr:5432/incluzor')
df = pd.read_sql('select * from lexique_olfq;', engine)
print(df)


# Aouter un mot si le mot n'existe pas déjà
def add_word(masc):
    # TODO. utilise un helper class pour la création des terminaisons
    terminaisons = [
                  {"terminaisons": ["teur"],  "nom": "teur"},  # 3.3
                  {"terminaisons": ["eur"], "nom": "eur"},  # 3.2
                  {"terminaisons": ["a", "o", "u"], "nom": "a,o,u"},  # 2.c
                  {"terminaisons": ["i", "é"], "nom": "i,é"},  # 2.c
                  {"terminaisons": ["e"], "nom": "e"},  # 2.b
               ]

    from mots.models import Mot
    from mots.models import FlexionFéminine
    import string
    consonnes = [l for l in string.ascii_lowercase if l not in ["a", "e", "i", "o", "u"]]

    terminaisons.append({"terminaisons": consonnes, "nom": "consonne"})
    print(terminaisons)

    masc_sing = masc
    # TODO: trouver le pluriel dans une dictionnaire
    masc_plur = masc+"s"

    args = {"masculin_singulier": masc_sing,
            "masculin_pluriel": masc_plur}

    # Source
    args["source"] = "olfq"
    # how to signal the plural's source since it will not be the same source.

    # Fréquence (default None, on va les ajouter plus tard)
    args["fréquence"] = {}

    # Notes
    commentaires = []
    commentaires_internes = []

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
    validation = "à traiter"
    args["validation"] = validation

    # Ajouter des infos sur la création du mot dans les commentaires
    args["commentaires_internes"] = commentaires_internes

    # Créer le mot
    mot = Mot(**args)
    mot.save()
    return mot

# Pour chaque ligne des résultats, trouver le masculin, puis ajouter les 
# féminins s'il y a besoin.
for idx, row in df.iterrows():
    masc = row["Masculin"]
    fems = [f.split("(")[0].strip() for f in row["Féminin"].split(";")]

    mots = Mot.objects.filter(masculin_singulier=masc)
    if len(mots) == 0:
        print("Créer: ", masc)
        mot = add_word(masc)
    elif len(mots) > 1:
        raise
    else:
        mot = mots[0]

    fem_existants = FlexionFéminine.objects.filter(mot_ref__pk=mot.pk).all()
    fem_existants_s = [fe.singulier for fe in fem_existants]
    print(masc, fem_existants_s)

    for flexion in fems:
        if flexion not in fem_existants_s:
            singulier = flexion
            # TODO: trouver le pluriel dans une dictionnaire
            pluriel = flexion+"s"
            fréquence = {}
            validation = "à traiter"
            commentaires_internes = []
            source = "olfq"

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
            print("Added: " + flexion)
            flex.save()

        print("-")
