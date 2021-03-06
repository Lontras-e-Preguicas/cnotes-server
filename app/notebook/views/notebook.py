from drf_yasg.openapi import Parameter
from drf_yasg.utils import swagger_auto_schema
from rest_framework import authentication, permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Notebook, Member
from notebook.serializers.folder import FolderSerializer
from notebook.serializers.member import MemberSerializer
from notebook.serializers.notebook import NotebookSerializer
from notebook.serializers.search import SearchResult, SearchResultSerializer


class NotebookRolePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj: Notebook):

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == 'destroy':
            if request.user != obj.owner:
                return False
        else:
            membership = obj.members.get(user=request.user)
            if membership.role != Member.Roles.ADMIN:
                return False

        return True


class NotebookViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                      mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    serializer_class = NotebookSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, NotebookRolePermission)
    queryset = Notebook.objects.all()

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return self.queryset
        return Notebook.objects.filter(member__user=self.request.user,
                                       member__is_active=True)

    @swagger_auto_schema(
        responses={200: MemberSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        instance: Notebook = self.get_object()
        serializer = MemberSerializer(instance.members.filter(is_active=True), many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        responses={200: FolderSerializer()}
    )
    @action(detail=True, methods=['get'])
    def root(self, request, pk=None):
        instance: Notebook = self.get_object()
        serializer = FolderSerializer(instance.root_folder)
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[Parameter('q', 'query', required=True, type='string',
                                     description='_query_ de pesquisa (pode ser substituído pelo parâmetro `query`)')],
        responses={200: SearchResultSerializer()}
    )
    @action(detail=True, methods=['get'])
    def search(self, request, pk=None):
        instance: Notebook = self.get_object()
        query = request.query_params.get('q', None) or request.query_params.get('query', '')
        serializer = SearchResultSerializer(SearchResult(instance, query))
        return Response(serializer.data)
