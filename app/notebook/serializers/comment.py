from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from core.models import Comment, Member, User
from notebook.serializers.member import AuthorSerializer


class CommentSerializer(serializers.ModelSerializer):
    commenter = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'note', 'commenter', 'message', 'creation_date', 'solved')
        read_only_fields = ('id', 'creation_date')

    def validate(self, attrs):
        current_user: User = self.context['request'].user
        note = self.instance.note if self.instance else attrs[
            'note']  # If there's neither, this code point shouldn't be reached

        try:
            current_user_membership = current_user.memberships.get(notebook=note.notebook, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        if current_user_membership.is_banned:
            raise serializers.ValidationError(_('O usuário está banido do caderno'))

        if self.instance:
            if 'note' in attrs:
                raise serializers.ValidationError(_('Não é possível mover um comentário entre anotações'))
            if 'message' in attrs and self.instance.commenter != current_user_membership:
                raise exceptions.PermissionDenied()
            if 'solved' in attrs \
                    and self.instance.commenter != current_user_membership \
                    and current_user_membership.role == Member.Roles.MEMBER:
                raise exceptions.PermissionDenied()
        else:
            attrs['commenter'] = current_user_membership

        return attrs
