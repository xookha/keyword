from django.contrib import admin

from .models import Address, UrlPerm, UserPayment


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Register Address model to admin panel."""


@admin.register(UrlPerm)
class UrlPermUserAdmin(admin.ModelAdmin):
    """Register UrlPerm model to admin panel."""


@admin.register(UserPayment)
class PaymentAdmin(admin.ModelAdmin):
    """Register Payment model to admin panel."""
