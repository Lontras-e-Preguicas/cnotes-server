from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions

from core.models import Attachment, Member


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('id', 'note', 'uploaded_file', 'uploaded_at')

    def validate_uploaded_file(self, value):
        print(value)
        return value

    def validate(self, attrs):
        if self.instance:
            if 'note' in attrs:
                raise serializers.ValidationError('Não é possível mover um anexo entre anotações')
            note = self.instance.note
        else:
            note = attrs['note']

        current_user = self.context['request'].user

        try:
            current_user_membership = note.notebook.members.get(user=current_user, is_active=True)
        except Member.DoesNotExist:
            raise exceptions.ValidationError(_("Usuário não encontrado"))

        if current_user_membership.is_banned:
            raise exceptions.PermissionDenied(_("O usuário está banido do caderno"))

        if current_user_membership.role == Member.Roles.MEMBER and note.author != current_user_membership:
            raise exceptions.PermissionDenied()

        return attrs
