from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from core.models import Invite, User, Member, Notebook


class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'profile_picture')
        read_only_fields = fields


class SenderSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    profile_picture = serializers.CharField(source='user.profile_picture')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = Member
        fields = ('id', 'name', 'email', 'profile_picture')
        read_only_fields = fields


class InviteSerializer(serializers.ModelSerializer):
    receiver = ReceiverSerializer(read_only=True)
    sender = SenderSerializer(read_only=True)

    receiver_email = serializers.SlugRelatedField(queryset=User.objects.all(), source="receiver", slug_field="email",
                                                  write_only=True)
    sender_notebook = serializers.PrimaryKeyRelatedField(queryset=Notebook.objects.all(), source="sender.notebook",
                                                         write_only=True)

    class Meta:
        model = Invite
        fields = ('id', 'sender', 'receiver', 'invite_date', 'receiver_email', 'sender_notebook')

    def validate(self, attrs):
        current_user: User = self.context['request'].user
        notebook: Notebook = attrs['sender']['notebook']

        try:
            current_membership = notebook.members.get(user=current_user, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        if current_membership.is_banned or current_membership.role == Member.Roles.MEMBER:
            raise serializers.ValidationError(_('Apenas moderadores e administradores podem convidar usuários'))

        receiver: User = attrs['receiver']

        if notebook.members.filter(user=receiver).count() != 0:
            raise serializers.ValidationError(_('Esse usuário já é membro do caderno'))

        if receiver.invites.filter(sender__notebook=notebook).count() != 0:
            raise serializers.ValidationError(_('Esse usuário já foi convidado para o caderno'))

        attrs['sender'] = current_membership
        attrs['receiver'] = receiver

        return attrs
