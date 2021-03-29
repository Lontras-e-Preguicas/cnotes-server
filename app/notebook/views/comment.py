from rest_framework import viewsets, permissions, authentication, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from notebook.serializers.comment import CommentSerializer
from core.models import Comment, Notebook, Member


class ModifyCommentPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Comment):
        if request.method in permissions.SAFE_METHODS:
            return True

        membership = obj.note.notebook.members.get(user=request.user)

        if obj.commenter != membership and membership.role == Member.Roles.MEMBER:
            return False

        return True


class CommentViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    serializer_class = CommentSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, ModifyCommentPermission)
    queryset = Comment.objects.all()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset

        user_notebooks = Notebook.objects.filter(member__user=self.request.user,
                                                 member__is_active=True)
        return self.queryset.filter(commenter__notebook__in=user_notebooks)

    @action(detail=True, methods=['post'])
    def solve(self, request, pk=None, solved=True):
        data = {
            'solved': solved
        }
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unsolve(self, request, pk=None):
        return self.solve(request, pk=pk, solved=False)
