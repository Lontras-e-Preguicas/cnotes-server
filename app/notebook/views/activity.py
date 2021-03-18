from rest_framework import viewsets, mixins, permissions, authentication, status
from rest_framework.decorators import action
from rest_framework.response import Response

from notebook.serializers.activity import ActivitySerializer
from core.models import Activity


class ActivityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    serializer_class = ActivitySerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Activity.objects.all()

    def get_queryset(self):
        current_user = self.request.user
        return self.queryset.filter(user=current_user)

    @action(detail=True, methods=['post'])
    def see(self, request, pk=None):
        instance: Activity = self.get_object()
        instance.seen = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def unsee(self, request, pk=None):
        instance: Activity = self.get_object()
        instance.seen = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
