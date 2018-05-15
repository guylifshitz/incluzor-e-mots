# open file & create csvreader
import pandas as pd

# import the relevant model
from mots.models import Mot

Mot.objects.all().delete()

raw_data = pd.read_csv("../../raw-data/lexique.csv")
raw_data = raw_data[0:]
raw_data["masculin"] = raw_data["masculin"].fillna("")
raw_data["masculin pluriel"] = raw_data["masculin pluriel"].fillna("")

for idx, row in raw_data.iterrows():
    # add some custom validation\parsing for some of the fields

    print(idx)
    print(row["masculin"])

    masculin_sings = str(row["masculin"]).split(",")

    print(row["masculin pluriel"])

    masculin_plurs = str(row["masculin pluriel"]).split(",")

    args = {"masculin_singulier": masculin_sings[0],
            "masculin_pluriel": masculin_plurs[0]}

    # for i in range(1, len(masculin_sings)):
    #     args["masculin_singulier_{c}".format(c=i+1)] = masculin_sings[i]

    # for i in range(1, len(masculin_plurs)):
    #     args["masculin_pluriel_{c}".format(c=i+1)] = masculin_plurs[i]

    args["masculin_sinuglier_autres"] = masculin_sings[1:]
    args["masculin_pluriel_autres"] = masculin_plurs[1:]

    args["fréquence"] = {"ngrams":{"singulier":None, "pluriel":None}, "google":{"singulier":None, "pluriel":None}}

    mot = Mot(**args)
    mot.save()
