from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializes the User model"""

    class Meta:
        model = User
        fields = ('email', 'name', 'password', 'bio', 'profile_picture')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Creates new User with password"""
        return User.objects.create_user(**validated_data)  # The default create method does not use set_password
