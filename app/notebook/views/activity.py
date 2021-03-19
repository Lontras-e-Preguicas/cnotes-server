from rest_framework import viewsets, mixins, permissions, authentication, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema, no_body

from notebook.serializers.activity import ActivitySerializer
from core.models import Activity


class ActivityViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    serializer_class = ActivitySerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Activity.objects.all()

    def get_queryset(self):
        current_user = self.request.user
        if current_user.is_anonymous:
            return self.queryset
        return self.queryset.filter(user=current_user)

    @swagger_auto_schema(
        request_body=no_body,
        responses={204: ''}
    )
    @action(detail=True, methods=['post'])
    def see(self, request, pk=None):
        instance: Activity = self.get_object()
        instance.seen = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=no_body,
        responses={204: ''}
    )
    @action(detail=True, methods=['post'])
    def unsee(self, request, pk=None):
        instance: Activity = self.get_object()
        instance.seen = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
