from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CallbackViewset, CaseViewset, EventViewset

app_name = 'api'

router = DefaultRouter()
router.register(r"callback", CallbackViewset, basename="callback")
router.register(r"cases", CaseViewset, basename="cases")
router.register(r"events", EventViewset, basename="events")

urlpatterns = [
] + router.urls