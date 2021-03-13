from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import NoteGroup, Member
from .utils import SerializedPKRelatedField
from .note import RelatedNoteSerializer


class RelatedNoteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteGroup
        fields = ('id', 'title')
        read_only_fields = ('id',)


class NoteGroupSerializer(serializers.ModelSerializer):
    notes = SerializedPKRelatedField(serializer=RelatedNoteSerializer, read_only=True, many=True, default=[])

    class Meta:
        model = NoteGroup
        fields = ('id', 'title', 'parent_folder', 'notes')
        read_only_fields = ('id',)

    def validate(self, attrs):
        current_user = self.context['request'].user

        if 'parent_folder' in attrs:
            parent_folder = attrs['parent_folder']
        elif self.instance:
            parent_folder = self.instance.parent_folder
        else:
            raise serializers.ValidationError(_('parent_folder é obrigatório'))

        try:  # Check membership
            membership = Member.objects.get(notebook=parent_folder.notebook, user=current_user, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        if membership.is_banned:  # Check ban
            raise serializers.ValidationError(_('O usuário está banido do caderno'))

        if self.instance:
            if self.instance.notebook != parent_folder.notebook:  # Check notebook change
                raise serializers.ValidationError(_('Não é permitido mover conjuntos de anotações entre cadernos'))

        return attrs
