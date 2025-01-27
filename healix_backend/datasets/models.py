from django.db import models


class Patient(models.Model):
    """
    Patient model to store demographic and vital sign details.
    """

    id = models.CharField(primary_key=True, max_length=255)
    gender = models.CharField(max_length=10, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)  # Derived field
    bmi = models.FloatField(null=True, blank=True)
    sys_bp = models.FloatField(
        null=True, blank=True, verbose_name="Systolic Blood Pressure"
    )
    dia_bp = models.FloatField(
        null=True, blank=True, verbose_name="Diastolic Blood Pressure"
    )
    heart_rate = models.FloatField(null=True, blank=True)
    bp_category = models.CharField(
        max_length=20, null=True, blank=True
    )  # Derived field

    def __str__(self):
        return f"Patient {self.id}"


class Condition(models.Model):
    """
    Condition model linked to patients.
    """

    # Removed id = models.CharField(primary_key=True, max_length=255) - Let Django auto-generate PK
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="conditions"
    )
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Condition {self.description} for Patient {self.patient.id}"


class Observation(models.Model):
    """
    Observation model for vital signs and other observations linked to patients.
    """

    # Removed id = models.CharField(primary_key=True, max_length=255) - Let Django auto-generate PK
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="observations"
    )
    description = models.TextField(null=True, blank=True)
    value = models.FloatField(null=True, blank=True)
    units = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Observation {self.description} for Patient {self.patient.id}"
