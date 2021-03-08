from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import Member, NoteGroup, Note


# Change to default serializer?

class NoteSerializer(serializers.ModelSerializer):
    """Serializes Note model"""

    class Meta:
        model = Note
        fields = ('id', 'author', 'note_group', 'title', 'creation_date', 'content')
        extra_kwargs = {
            'id': {
                'read_only': True
            },
            'author': {
                'read_only': True
            }
        }

    def validate(self, attrs):
        membership = Member.objects.get(id=attrs['author'])
        note_group = NoteGroup.objects.get(id=attrs['note_group'])

        if membership is None:
            raise serializers.ValidationError(_('Membro inexistente'))

        if note_group is None:
            raise serializers.ValidationError(_('Conjunto de anotação inexistente'))

        if membership.notebook.id != note_group.parent_folder.notebook.id:
            raise serializers.ValidationError(_('Membro inválido para tal conjunto de anotação'))
