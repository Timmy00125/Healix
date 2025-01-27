from django.urls import path
from .views import (
    ConditionPrevalenceByLocation,
    AvgBMIByLocation,
    BloodPressureDistribution,
)

urlpatterns = [
    path(
        "condition-prevalence/",
        ConditionPrevalenceByLocation.as_view(),
        name="condition-prevalence",
    ),
    path(
        "avg-bmi-by-location/", AvgBMIByLocation.as_view(), name="avg-bmi-by-location"
    ),
    path(
        "bp-distribution/", BloodPressureDistribution.as_view(), name="bp-distribution"
    ),
]
