from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AgentApplicationViewSet

router = DefaultRouter()
router.register(r"applications", AgentApplicationViewSet, basename="agent-application")

app_name = "agents"

urlpatterns = [
    path("", include(router.urls)),
]
