from django.shortcuts import render

import pandas as pd
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Patient, Condition, Observation
from .serializers import PatientSerializer, ConditionSerializer, ObservationSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows patients to be viewed and edited.
    """

    queryset = Patient.objects.all().order_by("id")
    serializer_class = PatientSerializer


class ConditionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows conditions to be viewed and edited.
    """

    queryset = Condition.objects.all().order_by("id")
    serializer_class = ConditionSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows observations to be viewed and edited.
    """

    queryset = Observation.objects.all().order_by("id")
    serializer_class = ObservationSerializer


class DatasetUploadViewSet(viewsets.ViewSet):
    """
    API endpoint for uploading Synthea CSV datasets.
    """

    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=["post"], url_path="patients")
    def upload_patients(self, request):
        """Upload and process patients.csv."""
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_csv(file_obj)
            for index, row in df.iterrows():
                # Data Preprocessing and Cleaning
                birthdate = (
                    pd.to_datetime(row["BIRTHDATE"]).date()
                    if pd.notnull(row["BIRTHDATE"])
                    else None
                )
                age = (
                    (pd.to_datetime("today").year - birthdate.year)
                    if birthdate
                    else None
                )
                patient_data = {
                    "id": row["Id"],
                    "gender": row["GENDER"],
                    "birthdate": birthdate,
                    "age": age,
                    # Add other patient related fields from CSV if needed in Patient model
                }
                serializer = PatientSerializer(data=patient_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"status": "Patients data uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="conditions")
    def upload_conditions(self, request):
        """Upload and process conditions.csv."""
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_csv(file_obj)  # Or sep=',' if comma-separated

            for index, row in df.iterrows():
                # Data Preprocessing and Cleaning
                patient_id = row["PATIENT"]
                start_date_str = row["START"]
                start_date = (
                    pd.to_datetime(start_date_str).date()
                    if pd.notnull(start_date_str)
                    else None
                )

                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    return Response(
                        {
                            "error": f"Patient with ID {patient_id} not found for condition."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                condition_data = {
                    # Removed 'id': row['Id'], - No condition ID from CSV, Django will auto-generate PK
                    "patient": patient.id,
                    "description": row["DESCRIPTION"],
                    "start_date": start_date,
                }
                serializer = ConditionSerializer(data=condition_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"status": "Conditions data uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="observations")
    def upload_observations(self, request):
        """Upload and process observations.csv."""
        file_obj = request.FILES.get("file")
        if file_obj is None:
            return Response(
                {"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_csv(file_obj)  # Or sep=',' if comma-separated

            for index, row in df.iterrows():
                # Data Preprocessing and Cleaning
                patient_id = row["PATIENT"]
                date_str = row["DATE"]
                date = pd.to_datetime(date_str).date() if pd.notnull(date_str) else None
                value = row["VALUE"] if pd.notnull(row["VALUE"]) else None
                units = row["UNITS"] if pd.notnull(row["UNITS"]) else None

                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    return Response(
                        {
                            "error": f"Patient with ID {patient_id} not found for observation."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                observation_data = {
                    # Removed 'id': str(uuid.uuid4()), - No need to generate ID, Django auto-generates PK
                    "patient": patient.id,
                    "description": row["DESCRIPTION"],
                    "value": value,
                    "units": units,
                    "date": date,
                }
                serializer = ObservationSerializer(data=observation_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {"status": "Observations data uploaded successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
