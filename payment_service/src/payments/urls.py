from django.urls import path

from . import views

urlpatterns = [
    path(
        'info',
        views.PayView.as_view(),
        name='payment_info'
    ),
    path(
        'create/<int:pk>',
        views.PaymentCreateView.as_view(),
        name='payment_create'
    ),
]
