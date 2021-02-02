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