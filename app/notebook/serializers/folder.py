from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError as DjangoValidationError

from core.models import Folder, Member

from .utils import SerializedPKRelatedField

class ChildFolderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Folder
        fields = ('id', 'title')
        read_only_fields = fields


class FolderSerializer(serializers.ModelSerializer):
    sub_folders = SerializedPKRelatedField(serializer=ChildFolderSerializer, default=[], many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'title', 'notebook', 'parent_folder', 'sub_folders')
        read_only_fields = ('id',)
        extra_kwargs = {'notebook': {'required': False}}

    def validate_parent_folder(self, value):
        """prevent empty parent_folder"""
        if value is None:
            raise serializers.ValidationError(_('parent_folder não pode ser nulo'))
        return value

    def validate(self, attrs):
        current_user = self.context['request'].user

        # Field auto-fill and notebook/parent_folder integrity
        if 'notebook' in attrs:
            notebook = attrs['notebook']
            if 'parent_folder' not in attrs:
                attrs['parent_folder'] = notebook.root_folder

        if 'parent_folder' in attrs:  # Normalize notebook field if parent_folder exists
            parent_folder: Folder = attrs['parent_folder']
            attrs['notebook'] = parent_folder.notebook
        else:
            if not self.instance:
                raise serializers.ValidationError(_('O campo parent_folder ou o campo notebook são obrigatórios'))
            parent_folder = self.instance.parent_folder

        try:  # Check membership
            membership = Member.objects.get(notebook=parent_folder.notebook, user=current_user, is_active=True)
        except Member.DoesNotExist:
            raise serializers.ValidationError(_('O usuário não é membro do caderno'))

        if membership.is_banned:  # Check ban
            raise serializers.ValidationError(_('O usuário está banido do caderno'))

        if self.instance:
            if self.instance.parent_folder is None:  # Check root
                raise serializers.ValidationError(_('Não é permitido modificar a pasta raiz'))
            if self.instance.notebook != parent_folder.notebook:  # Check notebook change
                raise serializers.ValidationError(_('Não é permitido mover pastas entre cadernos'))
            if parent_folder.id == self.instance.id:  # Check self-reference
                raise serializers.ValidationError(_('Não é permitido auto referência de pastas'))

            try:
                self.instance.clean(parent_folder=parent_folder)  # Check circular reference and max_depth
            except DjangoValidationError as err:
                raise serializers.ValidationError(err.message)

        return attrs
