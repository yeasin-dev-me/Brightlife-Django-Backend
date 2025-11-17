from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MembershipApplicationViewSet

router = DefaultRouter()
router.register(r'applications', MembershipApplicationViewSet, basename='membership-application')

app_name = 'membership'

urlpatterns = [
    path('', include(router.urls)),
]
