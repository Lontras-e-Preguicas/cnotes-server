from rest_framework import authentication, permissions, viewsets, mixins

from notebook.serializers.note import NoteSerializer
from core.models import Note, Notebook, Member


class ModifyNotePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Note):
        membership = request.user.memberships.get(notebook=obj.notebook)

        if request.method in permissions.SAFE_METHODS:
            return True

        if membership.is_banned or (obj.author != membership and membership.role == Member.Roles.MEMBER):
            return False

        return True


class NoteViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin):
    serializer_class = NoteSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, ModifyNotePermission)
    queryset = Note.objects.all()

    def get_queryset(self):
        # Limit user access to only their notebooks
        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)
        queryset = self.queryset.filter(note_group__parent_folder__notebook__in=user_notebooks)
        return queryset
