from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions

from core.models import Notebook, Member


class NotebookSerializer(serializers.ModelSerializer):
    root_folder = serializers.PrimaryKeyRelatedField(read_only=True)
    member_count = serializers.SerializerMethodField()

    def get_member_count(self, obj: Notebook):
        return obj.members.count()

    class Meta:
        model = Notebook
        fields = ('id', 'title', 'creation_date', 'root_folder', 'member_count')

    def validate(self, attrs):
        current_user = self.context['request'].user

        if self.instance:
            try:
                current_membership: Member = self.instance.members.get(user=current_user, is_active=True)
            except Member.DoesNotExist:
                raise serializers.ValidationError(_('O usuário não é membro do caderno'))

            if current_membership.role != Member.Roles.ADMIN:
                raise exceptions.PermissionDenied()
        else:
            attrs['owner'] = current_user

        return attrs

    def create(self, validated_data):
        return Notebook.objects.create_notebook(**validated_data)
