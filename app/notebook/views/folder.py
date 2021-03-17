from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions, mixins, viewsets, permissions, authentication
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Folder, Member, User
from notebook.serializers.folder import FolderSerializer


class FolderRolePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Folder):
        if view.action != 'destroy':
            return True

        membership = obj.notebook.members.get(user=request.user)

        if membership.role == Member.Roles.MEMBER:
            return False

        return True


@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_description="Ou `notebook`, ou `parent_folder` são necessários. `parent_folder` sobrescreve `notebook`"))
class FolderViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                    mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = FolderSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, FolderRolePermission)
    queryset = Folder.objects.all()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset
        current_user: User = self.request.user
        return self.queryset.filter(notebook__member__user=current_user, notebook__member__is_active=True)

    @swagger_auto_schema(
        methods=['get'],
        operation_description="Endpoint em análise, pode ser ***modificado*** ou ***removido*** futuramente.",
        manual_parameters=[
            Parameter(
                'notebook',
                'query',
                required=True,
                type='string <uuid>',
                description="ID do caderno a se obter a pasta raiz.")],
        responses={
            200: FolderSerializer()})
    @action(detail=False, methods=['get'], url_name='root')
    def root(self, request):
        notebook_id = request.query_params.get('notebook', None)

        if notebook_id is None:
            raise exceptions.ValidationError({'notebook': [_('O campo notebook é obrigatório')]})

        try:
            instance = self.get_queryset().get(notebook_id=notebook_id, parent_folder=None)
        except Folder.DoesNotExist:
            raise exceptions.ValidationError({'notebook': [_('O caderno não foi encontrado')]})

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
