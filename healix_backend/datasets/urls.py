from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet,
    ConditionViewSet,
    ObservationViewSet,
    DatasetUploadViewSet,
)

router = DefaultRouter()
router.register(r"patients", PatientViewSet)
router.register(r"conditions", ConditionViewSet)
router.register(r"observations", ObservationViewSet)
router.register(
    r"upload", DatasetUploadViewSet, basename="upload"
)  # Register upload viewset

urlpatterns = [
    path("", include(router.urls)),
]
