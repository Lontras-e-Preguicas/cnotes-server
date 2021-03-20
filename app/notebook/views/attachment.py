from django.shortcuts import redirect
from rest_framework import authentication, permissions, viewsets, mixins

from core.models import Notebook, Attachment, Member
from notebook.serializers.attachment import AttachmentSerializer


class DestroyAttachmentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Attachment):
        if view.action != 'destroy':
            return True

        try:
            current_user_membership = obj.note.notebook.members.get(user=request.user, is_active=True)
        except Member.DoesNotExist:
            return False

        if current_user_membership.is_banned or (
                current_user_membership.role == Member.Roles.MEMBER and obj.note.author != current_user_membership):
            return False

        return True


class AttachmentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = AttachmentSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, DestroyAttachmentPermission)
    queryset = Attachment.objects.all()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset
        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)
        queryset = self.queryset.filter(note__note_group__parent_folder__notebook__in=user_notebooks)
        return queryset


class OpenAttachmentViewSet(viewsets.GenericViewSet):
    serializer_class = AttachmentSerializer
    authentication_classes = ()
    permission_classes = ()
    queryset = Attachment.objects.all()

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return redirect(serializer.data['uploaded_file'])
