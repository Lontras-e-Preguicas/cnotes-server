from rest_framework import authentication, permissions, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from notebook.serializers.notebook import NotebookSerializer
from notebook.serializers.member import MemberSerializer

from core.models import Notebook, Member, User

class NotebookViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = Notebook.objects.all()
    serializer_class = NotebookSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        # Limit user access to only their notebooks
        if self.request.user.is_anonymous:
            return self.queryset
        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)

class NotebookRolePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Notebook):
        if view.action != 'destroy':
            return True

        membership = obj.notebook.members.get(user=request.user)

        if membership.role == Member.Roles.MEMBER:
            return False

        return True