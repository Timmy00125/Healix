from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Patient, Condition, Observation

admin.site.register(Patient)
admin.site.register(Condition)
admin.site.register(Observation)
