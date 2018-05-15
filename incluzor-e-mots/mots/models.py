from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django import forms


class Mot(models.Model):
    """
    Class pour les mots.
    TODO: ajouter les autres flexions masculines
    """

    masculin_singulier = models.CharField(max_length=100, blank=False)
    masculin_pluriel = models.CharField(max_length=100, blank=False)

    masculin_sinuglier_autres = ArrayField(
        models.CharField(max_length=100, blank=False), null=True
    )

    masculin_pluriel_autres = ArrayField(
        models.CharField(max_length=100, blank=False), null=True
    )

    fréquence = JSONField(null=True)

    # Terminaison du mot
    TERMINAISONS = (
        ("e", "e"),
        ("eur", "eur"),
    )

    terminaison = models.CharField(max_length=25, choices=TERMINAISONS,
                                   help_text="Catégorie de la terminaison du mot",
                                   blank=True)

    # Notes (internes + externes)
    notes_internes = ArrayField(
            models.TextField(blank=False), null=True
    )

    note_externe = models.TextField(blank=True, 
                                    help_text="Texte a montrer au utilisateur"
                                    )

    # Status validation
    VALIDATION_STATE = (
        ('générer', 'Générer'),
        ("à-valider", 'À valider'),
        ("erreur", 'Erreur signalé'),
        ("non-valide", 'Non-valide'),
        ("valide", 'Valide'),
    )

    validation = models.CharField(max_length=25, choices=VALIDATION_STATE, default="à-valider")

    # Created and modified times
    created_time = models.DateTimeField(auto_now_add=True)
    modified_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.masculin_singulier


class Flexion(models.Model):
    """
    Class pour les flexions
    """

    # Référence vers le mot
    mot = models.ForeignKey(Mot, on_delete=models.CASCADE)

    # singulier et pluriel du flexion
    singulier = models.CharField(max_length=100, blank=False)
    pluriel = models.CharField(max_length=100, blank=False)

    # Fréquence en JSON (pour chaque source, singulier et pluriel)
    fréquence = JSONField(null=True)

    # Les sources ou nous le trouvons
    dictionnaires = ArrayField(
            models.CharField(max_length=50, blank=True), null=  True
    )

    #JSONField(null=True)     # nom du dict, url, notes
    liens = JSONField(null=True)     # url, notes

    # Labels
    libelles = ArrayField(
            models.CharField(max_length=30, blank=True)
    )

    # Notes
    notes_internes = ArrayField(
            models.TextField(blank=False), null=True
    )

    note_externe = models.TextField(blank=True)

    # Validation status
    VALIDATION_STATE = (
        ('générer', 'Générer'),
        ("à-valider", 'À valider'),
        ("erreur", 'Erreur signalé'),
        ("non-valide", 'Non-valide'),
        ("valide", 'Valide'),
    )

    validation = models.CharField(max_length=30,
                                  blank=False,
                                  choices=VALIDATION_STATE,
                                  default='à-valider',
                                  )

    # Created et Modified date
    modified_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)


class FlexionMasculine(Flexion):
    pass


class FlexionFéminine(Flexion):
    pass
