from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

from core.models import Member, NoteGroup, Note, Notebook


class SerializerRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Field to represent a related field (FK) through a serializer on read
    ref: https://stackoverflow.com/a/52246232
    """

    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')
        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, value):
        if self.serializer:
            return self.serializer(value, context=self.context).data
        return super().to_representation(value)


class NoteAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    profile_picture = serializers.CharField(source='user.profile_picture')

    class Meta:
        model = Member
        fields = ('id', 'name', 'profile_picture')
        read_only_fields = fields


class NoteSerializer(serializers.ModelSerializer):
    """Serializes Note model"""
    rating = serializers.SerializerMethodField()
    author = SerializerRelatedField(queryset=Member.objects.all(), serializer=NoteAuthorSerializer)

    def get_rating(self, obj: Note):
        computed_rating = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        return computed_rating

    class Meta:
        model = Note
        fields = ('id', 'author', 'note_group', 'title', 'creation_date', 'content', 'rating')
        read_only_fields = ('author',)

    def validate(self, attrs):
        """Retrieve author and validate user membership"""

        notebook: Notebook = None

        if self.instance:
            notebook = self.instance.notebook

        if 'note_group' in attrs:
            new_note_group = attrs['note_group']
            new_notebook = new_note_group.notebook

            # Check if the notebook is changing
            if notebook is not None and new_notebook != notebook:
                raise exceptions.ValidationError({'note_group': [_('Não é permitido mover uma anotação entre cadernos')]})

            notebook = new_notebook

        try:
            # Check if the user is a notebook member
            membership: Member = self.context['request'].user.memberships.get(notebook=notebook, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        # Check if the user can modify any notebook info
        if membership.is_banned:
            raise exceptions.PermissionDenied()

        if self.instance:
            # Check if the user is modifying another member's note and if it has the role for it
            if self.instance.author != membership and membership.role == Member.Roles.MEMBER:
                raise serializers.ValidationError(_('Um membro não pode modificar a anotação de outro usuário'))
        else:
            attrs['author'] = membership

        return attrs
