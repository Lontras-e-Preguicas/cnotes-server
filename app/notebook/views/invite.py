from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, authentication, mixins, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Invite, Notebook, Member
from notebook.serializers.invite import InviteSerializer


class ModifyInvitePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Invite):
        if view.action == 'destroy':
            user = request.user
            try:
                notebook_membership = obj.sender.notebook.members.get(user=user)
                if notebook_membership.role == Member.Roles.MEMBER:
                    return False
            except Member.DoesNotExist:
                return False

        if view.action in ('accept', 'deny'):
            if obj.receiver != request.user:
                return False

        return True


class InviteViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                    mixins.RetrieveModelMixin):
    serializer_class = InviteSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, ModifyInvitePermission)
    queryset = Invite.objects.all()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset

        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)
        return self.queryset.filter(Q(receiver=self.request.user) | Q(sender__notebook__in=user_notebooks))

    @swagger_auto_schema(
        methods=['get'],
        manual_parameters=[
            Parameter(
                'notebook',
                'query',
                required=True,
                type='string <uuid>',
                description="ID do caderno a se obter os convites pendentes.")],
        responses={
            200: InviteSerializer(many=True)})
    @action(detail=False, methods=['get'])
    def pending(self, request):
        notebook_id = request.query_params.get('notebook', None)
        try:
            notebook = Notebook.objects.filter(member__user=self.request.user,
                                               member__is_active=True).get(id=notebook_id)
        except Notebook.DoesNotExist:
            raise exceptions.NotFound(_('Caderno não encontrado'))
        except DjangoValidationError as ex:
            raise exceptions.ValidationError({'detail': ex.messages})

        invites = self.queryset.filter(sender__notebook=notebook)
        invite_serializer = self.get_serializer(invites, many=True)
        return Response(invite_serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        instance: Invite = self.get_object()
        instance.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        instance: Invite = self.get_object()
        instance.deny()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def received(self, request):
        received_queryset = self.queryset.filter(receiver=self.request.user)
        serializer = self.get_serializer(received_queryset, many=True)
        return Response(serializer.data)
