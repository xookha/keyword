from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register('all', views.AddressViewSet, base_name='addresses')

urlpatterns = router.urls

urlpatterns += [
    path(
        'create',
        views.AddressCreateView.as_view(),
        name='create_address'
    ),
    path(
        'update-keywords/<int:pk>',
        views.UpdateAddressKeywordsView.as_view(),
        name='update_address_keywords'
    ),
    path(
        'delete/<int:pk>',
        views.AddressDestroyView.as_view(),
        name='delete_address'
    ),
    path(
        'update-keywords-callback/<int:pk>',
        views.AddressKeywordsCallbackView.as_view(),
        name='update_address_keywords_callback'
    ),
    path(
        'update-payment-callback/<int:pk>',
        views.PaymentCallbackView.as_view(),
        name='update_payment_callback'
    ),
]
