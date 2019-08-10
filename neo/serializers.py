from rest_framework import serializers
from . import models

class Symptom(serializers.ModelSerializer):
    class Meta:
        model = models.Symptom
        fields = ('name','ar_name')