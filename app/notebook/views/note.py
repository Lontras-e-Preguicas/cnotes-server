from django.core.exceptions import ValidationError

from rest_framework import authentication, permissions, viewsets, mixins, exceptions

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
                  mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = NoteSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, ModifyNotePermission)
    queryset = Note.objects.all()

    def get_queryset(self):
        # Limit user access to only their notebooks
        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)
        queryset = self.queryset.filter(note_group__parent_folder__notebook__in=user_notebooks)

        # Apply filters
        try:
            note_group = self.request.query_params.get('note_group', None)
            author = self.request.query_params.get('author', None)

            if note_group is not None:
                queryset = queryset.filter(note_group_id=note_group)
            if author is not None:
                queryset = queryset.filter(author_id=author)
        except ValidationError as ex:  # Change 500 in case of bad input to 400
            raise exceptions.ValidationError(detail={'detail': ex.messages[0]})

        # Order response
        queryset = queryset.order_by('creation_date')

        return queryset
