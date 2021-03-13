from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from core.models import Member, Note, Notebook

from .utils import SerializedPKRelatedField


class NoteAuthorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    profile_picture = serializers.CharField(source='user.profile_picture')

    class Meta:
        model = Member
        fields = ('id', 'name', 'profile_picture')
        read_only_fields = fields


class RelatedNoteSerializer(serializers.ModelSerializer):
    author = SerializedPKRelatedField(serializer=NoteAuthorSerializer, read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'author', 'title', 'creation_date', 'avg_rating')
        read_only_fields = fields


class NoteSerializer(serializers.ModelSerializer):
    """Serializes Note model"""
    class Meta:
        model = Note
        fields = ('id', 'author', 'note_group', 'title', 'creation_date', 'content', 'avg_rating')
        read_only_fields = ('author', 'avg_rating')

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
                raise exceptions.ValidationError(
                    {'note_group': [_('Não é permitido mover uma anotação entre cadernos')]})

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['author'] = NoteAuthorSerializer(instance.author).data

        return representation
