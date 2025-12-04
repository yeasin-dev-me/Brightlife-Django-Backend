from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MemberLoginView, MembershipApplicationViewSet

router = DefaultRouter()
router.register(
    r"applications", MembershipApplicationViewSet, basename="membership-application"
)

app_name = "membership"

urlpatterns = [
    # Member Login Endpoint
    path("login/", MemberLoginView.as_view(), name="member-login"),
    # Application CRUD routes
    path("", include(router.urls)),
]
