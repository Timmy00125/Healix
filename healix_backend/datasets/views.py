import pandas as pd
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Patient, Condition, Observation
from .serializers import PatientSerializer, ConditionSerializer, ObservationSerializer
import uuid


def clean_observation_value(value_str):
    """
    Cleans and converts a string value from the observation dataset to a float or None.
    Handles various formats including comma decimal separators, thousands separators,
    units attached, non-numeric prefixes, and missing value representations.
    """
    if pd.isna(value_str) or value_str in ["N/A", "NULL", "Missing", "Unknown", ""]:
        return None  # Handle missing values

    value_text = str(
        value_str
    ).strip()  # Convert to string and remove leading/trailing whitespace

    # Remove units if present (assuming unit is separated by space and at the end)
    parts = value_text.split()
    numeric_part_str = parts[0]

    # Remove thousands separators (commas and spaces)
    numeric_part_str = numeric_part_str.replace(",", "").replace(" ", "")

    # Replace comma decimal separator with period
    numeric_part_str = numeric_part_str.replace(",", ".")

    # Remove non-numeric prefixes like ">" or "<" (simply take the number after)
    if (
        numeric_part_str.startswith(">")
        or numeric_part_str.startswith("<")
        or numeric_part_str.startswith("=")
    ):
        numeric_part_str = numeric_part_str[1:]  # Remove the first character

    try:
        return float(numeric_part_str)
    except ValueError:
        return None  # Return None if still cannot convert to float


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
            df = pd.read_csv(file_obj)

            for index, row in df.iterrows():
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
            df = pd.read_csv(file_obj)  # Adjust separator if needed

            for index, row in df.iterrows():
                patient_id = row["PATIENT"]
                date_str = row["DATE"]
                date = pd.to_datetime(date_str).date() if pd.notnull(date_str) else None
                units = row["UNITS"] if pd.notnull(row["UNITS"]) else None

                # Clean and convert the 'VALUE' column using the dedicated function
                value = clean_observation_value(row["VALUE"])

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
                    "patient": patient.id,
                    "description": row["DESCRIPTION"],
                    "value": value,  # Use the cleaned value
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
