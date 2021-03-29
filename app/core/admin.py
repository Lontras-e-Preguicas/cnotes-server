from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    ordering = ('name', 'id',)
    readonly_fields = ('id', 'last_login',)
    list_display = ('name', 'email',)

    fieldsets = (
        (_('Campos padrões'), {
            'fields': ('id', 'name', 'email', 'bio', 'profile_picture',)
        }),
        (_('Senha'), {
            'fields': ('password',)
        }),
        (_('Permissões e estado'), {
            'description': _('O sistema de permissões padrão pode se encontrar com atuação limitada na API'),
            'fields': (
                'last_login',
                'is_active',
                'is_superuser',
                'is_staff',
                'groups',
                'user_permissions',
            )
        })
    )

    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('name', 'email', 'password1', 'password2',)
    }),)


@admin.register(models.Notebook)
class NotebookAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'creation_date')
    list_display = ('title', 'owner')

    fieldsets = ((None, {
        'fields': ('id', 'title', 'owner', 'creation_date')
    }),)


@admin.register(models.NoteGroup)
class NoteGroupAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('title', 'parent_folder')

    fieldsets = ((None, {
        'fields': ('id', 'title', 'parent_folder')
    }),)


@admin.register(models.Note)
class NoteAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'creation_date')
    list_display = ('title', 'author', 'note_group')

    fieldsets = ((None, {
        'fields': ('id', 'creation_date', 'author', 'note_group', 'title', 'content')
    }),)


admin.site.register(models.Folder)
admin.site.register(models.Member)
admin.site.register(models.Invite)
admin.site.register(models.Activity)
admin.site.register(models.Comment)
admin.site.register(models.Rating)
