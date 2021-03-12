from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, mixins, viewsets, permissions, authentication
from rest_framework.response import Response

from notebook.serializers.folder import FolderSerializer
from core.models import Folder, Member, User


class FolderRolePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Folder):
        if view.action != 'destroy':
            return True

        membership = obj.notebook.members.get(user=request.user)

        if membership.role == Member.Roles.MEMBER:
            return False

        return True


class FolderViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                    mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = FolderSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, FolderRolePermission)
    queryset = Folder.objects.all()

    def get_queryset(self):
        current_user: User = self.request.user
        return self.queryset.filter(notebook__member__user=current_user)

    def list(self, request):
        notebook_id = request.query_params.get('notebook', None)

        if notebook_id is None:
            raise exceptions.ValidationError({'notebook': _('O campo notebook é obrigatório')})

        instance = self.get_queryset().get(notebook_id=notebook_id, parent_folder=None)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
