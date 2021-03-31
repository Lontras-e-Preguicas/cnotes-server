from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation, tokens
from django.utils.translation import gettext_lazy as _

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializes the User model"""

    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'password', 'bio', 'profile_picture')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'trim_whitespace': False,
                'validators': [
                    password_validation.validate_password]}}

    # def validate_password(self, password):
    #     """Validate the password according to the password validators on settings"""
    #     password_validation.validate_password(password)
    #     return password

    def create(self, validated_data):
        """Creates new User with password"""
        return User.objects.create_user(**validated_data)  # The default create method does not use set_password

    def update(self, instance, validated_data):
        """Update User data with password"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for User authentication"""
    email = serializers.CharField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate an User"""
        email = attrs['email']
        password = attrs['password']

        user = authenticate(
            request=self.context['request'],
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(_('Falha ao autenticar usuário'), code='authentication')

        attrs['user'] = user
        return attrs


class CreatePasswordResetTokenSerializer(serializers.Serializer):
    """Serializer for creating a ResetToken"""
    email = serializers.EmailField()

    def validate(self, attrs):
        """Validate if the user exists"""
        email = attrs['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Usuário não encontrado'))

        attrs['user'] = user

        return attrs


class ConfirmPasswordResetTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.UUIDField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        validators=[password_validation.validate_password]
    )

    def validate(self, attrs):
        """Validate if the user exists and if the token is valid"""
        token = attrs['token']
        uid = attrs['uid']

        try:
            user = User.objects.get(id=uid)
        except User.DoesNotExist:
            raise serializers.ValidationError(_('UID inválido'))

        if not tokens.PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError(_('Token inválido ou expirado'))

        attrs['user'] = user

        return attrs

    def save(self):
        user: User = self.validated_data['user']
        password = self.validated_data['password']

        user.set_password(password)
        user.save()
        return user
