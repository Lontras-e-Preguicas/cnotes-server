from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from core.models import Member


class MemberSerializer(serializers.ModelSerializer):
    """Serializes the Member model"""
    email = serializers.CharField(source='user.email', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    bio = serializers.CharField(source='user.bio', read_only=True)
    profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)

    class Meta:
        model = Member
        fields = ('id', 'email', 'name', 'bio', 'profile_picture', 'notebook',
                  'role', 'member_since', 'is_active', 'is_banned')
        read_only_fields = ('id', 'notebook')

    def validate(self, value):
        target_member = self.instance
        try:
            # Get who is the actor
            actor_membership: Member = self.context['request'].user.memberships.get(
                notebook=target_member.notebook, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        # Check if the actor is banned from the notebook
        if actor_membership.is_banned:
            raise exceptions.PermissionDenied()

        # Check if the target is active
        if not target_member.is_active:
            raise serializers.ValidationError(_('Esse usuário não é mais membro do caderno.'))

        # Check if the role is changing
        if 'role' in value:
            new_role = value['role']

            # Check if the actor has the permission to change the role
            if new_role is not target_member.role and actor_membership.role == Member.Roles.MEMBER:
                raise serializers.ValidationError(_('Um membro não pode modificar o cargo de outro membro.'))

        # Check if someone is trying to ban/unban a member
        if 'is_banned' in value:
            ban = value['is_banned']

            # Check if the actor has the permission to ban/unban a member
            if actor_membership.role != Member.Roles.MEMBER and ban:
                # Check if the actor is trying to ban itself
                if target_member.user == actor_membership.user:
                    raise serializers.ValidationError(_('Nenhum usuário pode se banir'))
            elif ban:
                raise serializers.ValidationError(_('Um membro não pode banir outro.'))
            elif actor_membership.role == Member.Roles.MEMBER and not ban:
                raise serializers.ValidationError(_('Um membro não pode desbanir outro.'))

        # Check if someone is trying to kick a member or leave
        if 'is_active' in value:
            active = value['is_active']

            # Check if someone is trying to kick a member
            if target_member.user != actor_membership.user and not active:
                if actor_membership.role == Member.Roles.MEMBER:
                    raise serializers.ValidationError(_('Um membro não pode expulsar outro.'))

        # Check if the target is the owner of the notebook
        if target_member.user == target_member.notebook.owner:
            raise serializers.ValidationError(_('O dono do caderno não pode ter seus atributos modificados.'))

        return value
