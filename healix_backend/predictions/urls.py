from django.urls import path
from .views import ConditionPredictionView

urlpatterns = [
    path(
        "predict-condition/",
        ConditionPredictionView.as_view(),
        name="predict-condition",
    ),
]
