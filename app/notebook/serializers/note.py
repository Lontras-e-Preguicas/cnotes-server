from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import serializers, exceptions

from core.models import Member, Note, Notebook
from notebook.serializers.member import AuthorSerializer
from notebook.serializers.comment import CommentSerializer

EDIT_LOCK_DURATION = timedelta(seconds=10)


class RelatedNoteSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ('id', 'author', 'title', 'creation_date', 'avg_rating')
        read_only_fields = fields


class NoteSerializer(serializers.ModelSerializer):
    """Serializes Note model"""
    author = AuthorSerializer(read_only=True)
    last_edited_by = AuthorSerializer(read_only=True)
    comments = CommentSerializer(read_only=True, many=True)

    class Meta:
        model = Note
        fields = ('id', 'author', 'note_group', 'title', 'creation_date', 'content', 'avg_rating', 'comments', 'last_edited',
                  'last_edited_by')
        read_only_fields = ('avg_rating', 'last_edited')

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
            attrs['last_edited_by'] = membership  # Register last edit
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        # Check if the user can modify any notebook info
        if membership.is_banned:
            raise exceptions.PermissionDenied()

        if self.instance:
            # Check if the user is modifying another member's note and if it has the role for it
            if self.instance.author != membership and membership.role == Member.Roles.MEMBER:
                raise serializers.ValidationError(_('Um membro não pode modificar a anotação de outro usuário'))

            edit_timedelta = timezone.make_aware(datetime.utcnow()) - self.instance.last_edited
            if self.instance.last_edited_by not in (membership, None) and edit_timedelta < EDIT_LOCK_DURATION:
                raise serializers.ValidationError(_('Essa anotação está sendo editada por outro usuário'))
        else:
            attrs['author'] = membership

        return attrs
