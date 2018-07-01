from rest_framework import serializers
from .models import Mot, Flexion


class FlexionDétailsSerializer(serializers.ModelSerializer):
    fréquence = serializers.SerializerMethodField()

    class Meta:
        model = Flexion
        fields = ('__all__')

    def get_fréquence(self, obj):
        return obj.fréquence


class MotDétailsSerializer(serializers.ModelSerializer):
    flexions = FlexionDétailsSerializer(many=True)

    class Meta:
        model = Mot
        fields = ('__all__')


class MotMascSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mot
        fields = ('masculin_singulier',)
