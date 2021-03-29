from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import authentication, permissions, viewsets

from notebook.serializers.member import MemberSerializer
from core.models import Member


class MemberViewSet(viewsets.GenericViewSet):
    """ViewSet to list all members from a notebook"""

    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset

        current_user = self.request.user
        return self.queryset.filter(notebook__member__user=current_user, notebook__member__is_active=True)

    def list(self, request):
        notebook_id = request.GET.get("notebook")

        queryset = self.get_queryset().filter(notebook_id=notebook_id)
        serializer = MemberSerializer(queryset, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Change a member's role"""
        data = {
            "role": request.data.get('role', None)
        }

        instance: Member = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def kick_member(self, request, pk=None):
        """Kick a member from a notebook"""
        data = {
            "is_active": False
        }

        instance: Member = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def leave_notebook(self, request, pk=None):
        """Leave from a notebook"""
        data = {
            "is_active": False
        }

        instance: Member = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ban_member(self, request, pk=None):
        """Ban a member from a notebook"""
        data = {
            "is_banned": True
        }

        instance: Member = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unban_member(self, request, pk=None):
        """Unban a member from a notebook"""
        data = {
            "is_banned": False
        }

        instance: Member = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
