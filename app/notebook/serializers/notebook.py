from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, exceptions
from drf_yasg.utils import swagger_serializer_method

from core.models import Notebook, Member
from notebook.serializers.member import MemberSerializer


class NotebookSerializer(serializers.ModelSerializer):
    root_folder = serializers.PrimaryKeyRelatedField(read_only=True)
    member_count = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()

    def get_member_count(self, obj: Notebook):
        return obj.members.count()

    @swagger_serializer_method(serializer_or_field=MemberSerializer())
    def get_membership(self, obj: Notebook):
        membership = obj.members.get(user=self.context['request'].user)
        return MemberSerializer(membership).data

    class Meta:
        model = Notebook
        fields = ('id', 'title', 'creation_date', 'root_folder', 'member_count', 'membership')

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
