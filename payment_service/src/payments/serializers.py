from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer to create payment."""

    class Meta:
        model = Payment
        fields = ('id', 'amount', 'info', 'pay_id', 'callback_url')
