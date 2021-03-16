from rest_framework import authentication, permissions, viewsets, mixins, status, exceptions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from notebook.serializers.note import NoteSerializer
from notebook.serializers.rating import RatingSerializer
from core.models import Note, Notebook, Member, Rating


class ModifyNotePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj: Note):
        safe_actions = ('rating',)
        membership = request.user.memberships.get(notebook=obj.notebook)

        if request.method in permissions.SAFE_METHODS:
            return True

        if membership.is_banned:
            return False

        if view.action in safe_actions:
            return True

        if obj.author != membership and membership.role == Member.Roles.MEMBER:
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

    @action(detail=True, methods=['get', 'post'])
    def rating(self, request, pk=None):
        if request.method == 'GET':
            instance: Note = self.get_object()
            try:
                current_rating = instance.ratings.get(rater__user=request.user)
            except Rating.DoesNotExist:
                return Response({'avg_rating': instance.avg_rating, 'rating': None})
            return Response(RatingSerializer(current_rating).data)

        if request.method == 'POST':
            instance: Note = self.get_object()

            data = {
                'note': str(instance.id)
            }
            if 'rating' in request.data:
                data['rating'] = request.data['rating']

            rating_serializer = RatingSerializer(context=self.get_serializer_context(), data=data)

            try:
                current_rating = instance.ratings.get(rater__user=request.user)
                rating_serializer.instance = current_rating
            except Rating.DoesNotExist:
                pass

            rating_serializer.is_valid(raise_exception=True)
            rating_serializer.save()
            return Response(rating_serializer.data)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
