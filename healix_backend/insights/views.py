from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from datasets.models import Patient, Condition, Observation
from django.db.models import Count, Avg
import pandas as pd


class ConditionPrevalenceByLocation(APIView):
    """
    API endpoint to get condition prevalence by location (using patient's gender as location for example).
    """

    def get(self, request):
        condition_name = request.query_params.get("condition_name", None)
        if not condition_name:
            return Response({"error": "Condition name is required."}, status=400)

        # Aggregate conditions by patient gender (using gender as a proxy for location)
        prevalence_data = (
            Condition.objects.filter(description=condition_name)
            .values("patient__gender")
            .annotate(count=Count("patient"))
            .order_by("-count")
        )

        results = []
        for item in prevalence_data:
            results.append(
                {
                    "location": item[
                        "patient__gender"
                    ],  # Using gender as location proxy
                    "prevalence_count": item["count"],
                }
            )

        return Response(results)


class AvgBMIByLocation(APIView):
    """
    API endpoint to get average BMI by location (using patient's gender as location for example).
    """

    def get(self, request):
        # Aggregate average BMI by patient gender (using gender as a proxy for location)
        avg_bmi_data = (
            Patient.objects.values("gender")
            .annotate(avg_bmi=Avg("bmi"))
            .order_by("gender")
        )

        results = []
        for item in avg_bmi_data:
            results.append(
                {
                    "location": item["gender"],  # Using gender as location proxy
                    "average_bmi": item["avg_bmi"],
                }
            )
        return Response(results)


class BloodPressureDistribution(APIView):
    """
    API endpoint to get blood pressure distribution.
    """

    def get(self, request):
        bp_categories = ["normal", "hypertensive", "severe", "crisis"]
        distribution_data = Patient.objects.values("bp_category").annotate(
            count=Count("id")
        )

        results = []
        total_patients = Patient.objects.count()
        for item in distribution_data:
            category = item["bp_category"]
            if category in bp_categories:  # Ensure only valid categories are included
                percentage = (
                    (item["count"] / total_patients) * 100 if total_patients > 0 else 0
                )
                results.append(
                    {
                        "bp_category": category,
                        "count": item["count"],
                        "percentage": f"{percentage:.2f}%",
                    }
                )
        return Response(results)
