from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import PaymentProofStatusView, PaymentProofSubmitView, PaymentProofViewSet

# Router for admin viewset
router = DefaultRouter()
router.register(
    r"admin/payment-proofs", PaymentProofViewSet, basename="payment-proof-admin"
)

app_name = "payment"

urlpatterns = [
    # Public endpoints
    path("proof/", PaymentProofSubmitView.as_view(), name="payment-proof-submit"),
    path(
        "proof/<str:transaction_id>/",
        PaymentProofStatusView.as_view(),
        name="payment-proof-status",
    ),
    # Admin endpoints
    path("", include(router.urls)),
]
