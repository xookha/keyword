from django.conf import settings
from django.urls import reverse

from rest_framework import serializers

from .models import Address, UserPayment, UrlPerm


class AddressSerializer(serializers.ModelSerializer):
    """URL Address serializer."""

    class Meta:
        model = Address
        fields = ('id', 'url', 'is_processed',)
        extra_kwargs = {'is_processed': {'read_only': True}}


class AddressDetailSerializer(serializers.ModelSerializer):
    """URL Address detail serializer."""

    class Meta:
        model = Address
        fields = ('id', 'url', 'keywords', 'is_processed',)


class AddressUpdateSerializer(serializers.ModelSerializer):
    """URL Address serializer to update keywords."""

    class Meta:
        model = Address
        fields = ('id', 'keywords',)


class UserPaymentSerializer(serializers.ModelSerializer):
    """Serializer to collect data before payment."""
    pay_id = serializers.IntegerField(source='id')
    callback_url = serializers.SerializerMethodField()
    link = serializers.SerializerMethodField()

    class Meta:
        model = UserPayment
        fields = ('pay_id', 'amount', 'info', 'callback_url', 'link')

    def get_callback_url(self, obj):
        url = reverse("update_payment_callback", args=[obj.id])
        return f'{settings.SERVER_URL}{url}'

    def get_link(self, obj):
        link = f'{settings.PAYMENT_SERVICE_URL}api/payments/info?' \
            f'amount={int(obj.amount)}&info={obj.info}&pay_id={obj.id}&' \
            f'callback_url={self.get_callback_url(obj)}'
        return link


class UserPaymentUpdateSerializer(serializers.ModelSerializer):
    """Update payment via hook."""

    class Meta:
        model = UserPayment
        fields = ('status',)

    def update(self, instance, validated_data):
        """Update payment and perms."""
        instance = super().update(instance, validated_data)
        UrlPerm.objects.update_or_create(
            user=instance.user,
            defaults={'is_payed': True}
        )
        return instance
