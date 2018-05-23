from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django import forms


# Status validation
VALIDATION_STATES = (
    ('à traiter', 'À traiter '),
    ('doute', 'Doute'),
    ("valide", 'Valide'),
    ("erroné", 'Erroné'),
)


class CommonInfo(models.Model):
    """ 
    Chams commun au masculins et au féminins
    """

    # Fréquence en JSON (pour chaque source, singulier et pluriel)
    fréquence = JSONField(null=True)

    # Les sources ou nous le trouvons
    dictionnaires = JSONField(null=True)

    # Liens
    liens = ArrayField(
            models.CharField(max_length=250, blank=True), null=True,
    )

    # Commentaires (internes + externes)
    commentaires_internes = ArrayField(
            models.TextField(blank=False), null=True
    )

    commentaire_externe = models.TextField(blank=True)

    validation = models.CharField(max_length=25,
                                  choices=VALIDATION_STATES,
                                  blank=True)

    problème_signalé = models.BooleanField(default=False)
    visible = models.BooleanField(default=False)

    # Created and modified times
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    class Meta:
        # Ne créer pas une table pour ce modèle 
        abstract = True


class Mot(CommonInfo):
    """
    Class pour les mots.
    """

    masculin_singulier = models.CharField(max_length=100, blank=False)
    masculin_pluriel = models.CharField(max_length=100, blank=False)

    # Liste des autres formes masculines
    masculin_sinuglier_autres = ArrayField(
        models.CharField(max_length=100, blank=True), null=True,
        help_text="Autre flexions masculines, séparer par \",\". Même ordre que les pluriels.",
    )

    masculin_pluriel_autres = ArrayField(
        models.CharField(max_length=100, blank=True), null=True,
        help_text="Autre flexions masculines, séparer par \",\". Même ordre que les singuliers.",
    )

    # Terminaison du mot
    TERMINAISONS = (
        ("e", "e"),
        ("i,é", "i, é"),
        ("a,o,u", "a, o ,u"),
        ("eur", "eur"),
        ("teur", "teur"),
        ("consonne", "consonne")
    )

    terminaison = models.CharField(max_length=25, choices=TERMINAISONS,
                                   help_text="Catégorie de la terminaison du mot",
                                   blank=True)
    # source
    SOURCES = (
        ("admin", "Admin"),
        ("public", "Public"),
        ("import_spredsheet_01", "Import G-sheets"),
    )

    source = models.CharField(max_length=50, choices=SOURCES, blank=True)

    def féminine_flexions_count(self):
        return FlexionFéminine.objects.filter(mot_ref__pk=self.pk).count()

    def féminine_nonvalide_count(self):
        return FlexionFéminine.objects.filter(mot_ref__pk=self.pk).exclude(validation="valide").count()

    def __str__(self):
        return self.masculin_singulier


class Flexion(CommonInfo):
    """
    Class pour les flexions
    """

    # Référence vers le mot
    mot_ref = models.ForeignKey(Mot, on_delete=models.CASCADE)

    # singulier et pluriel du flexion
    singulier = models.CharField(max_length=100, blank=False)
    pluriel = models.CharField(max_length=100, blank=False)

    # Labels
    libelles = ArrayField(
            models.CharField(max_length=30, blank=True), null=True,
            help_text="ex. vieilli"
    )

    STRATÉGIES = (
        ("-e", "e"),
        ("-eusse", "eusse"),
        ("-oresse", "oresse"),
        # ...
    )

    stratégie = models.CharField(max_length=25, choices=STRATÉGIES,
                                 blank=True)

    afficher_info_stratégie = models.BooleanField(default=True)

    # source
    SOURCES = (
        ("Admin", "admin"),
        ("Public", "public"),
        ("Script : import G-sheets", "script_import_spredsheet_01"),
        ("Script : stratégie auto", "script_auto_règles"),
    )

    source = models.CharField(max_length=50, choices=SOURCES, blank=True)


class FlexionFéminine(Flexion):
    pass
