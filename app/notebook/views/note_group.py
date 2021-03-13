from rest_framework import authentication, permissions, viewsets, mixins

from core.models import NoteGroup, Member
from notebook.serializers.note_group import NoteGroupSerializer


class NoteGroupRolePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: NoteGroup):
        if view.action != 'destroy':
            return True

        membership = obj.notebook.members.get(user=request.user)

        if membership.role == Member.Roles.MEMBER:
            return False

        return True


class NoteGroupViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                       mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = NoteGroupSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, NoteGroupRolePermission,)
    queryset = NoteGroup.objects.all()

    def get_queryset(self):
        current_user = self.request.user
        return self.queryset.filter(parent_folder__notebook__member__user=current_user,
                                    parent_folder__notebook__member__is_active=True)
