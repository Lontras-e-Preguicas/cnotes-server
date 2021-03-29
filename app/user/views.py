from django.utils.translation import gettext_lazy as _

from rest_framework import authentication, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.settings import api_settings

from drf_yasg.utils import swagger_auto_schema

from user.serializers import UserSerializer, AuthTokenSerializer, CreatePasswordResetTokenSerializer, \
    ConfirmPasswordResetTokenSerializer
from user.signals import password_reset_request_signal


class CreateUserView(CreateAPIView):
    """
    View for creating a new User
    """
    serializer_class = UserSerializer


class CreateAuthTokenView(ObtainAuthToken):
    """
    View for generating a new Auth Token
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(RetrieveUpdateAPIView):
    """
    View for accessing and modifying authenticated User info
    """
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class PasswordResetViewset(viewsets.ViewSet):
    """
    ViewSet for managing password reset requests and executions
    """

    @swagger_auto_schema(
        request_body=CreatePasswordResetTokenSerializer,
        responses={200: ''},
    )
    @action(detail=False, methods=['post'], url_name='request')
    def password_reset(self, request):
        """Request password reset"""
        serializer = CreatePasswordResetTokenSerializer(data=request.data)

        if serializer.is_valid():
            password_reset_request_signal.send(self.__class__, user=serializer.validated_data['user'])

        return Response({'status': _('Solicitação de recuperação de senha enviada')})  # No data leakage

    @swagger_auto_schema(
        request_body=ConfirmPasswordResetTokenSerializer,
        responses={200: ''},
    )
    @action(detail=False, methods=['post'], url_name='confirm')
    def password_reset_confirm(self, request):
        """Confirm password reset"""
        serializer = ConfirmPasswordResetTokenSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response({'status': _('Senha alterada com sucesso')})
