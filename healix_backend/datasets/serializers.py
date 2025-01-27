from rest_framework import serializers
from .models import Patient, Condition, Observation


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = "__all__"


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = "__all__"
