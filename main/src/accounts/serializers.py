from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """User login serializer."""

    class Meta:
        model = User
        fields = ('id', 'username',)
