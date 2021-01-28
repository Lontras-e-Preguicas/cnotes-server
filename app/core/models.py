from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

import uuid
import os


def profile_picture_path(instance, filename):
    """Unique filename generation"""
    ext = filename.split('.')[-1]
    new_filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_pictures', new_filename)


class UserManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str, bio: str = None, **extra_fields):
        """Create an user from its fields"""
        if not email:
            raise ValueError(_('endereço de e-mail é obrigatório'))
        if not name:
            raise ValueError(_('nome é obrigatório'))
        if not password:
            raise ValueError(_('senha é obrigatória'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, bio=bio, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email: str, name: str, password: str, **extra_fields):
        """super user creation for django admin"""
        return self.create_user(
            email=email,
            name=name,
            password=password,
            is_superuser=True,
            is_staff=True,
            **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model, used for authentication"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)  # Required
    name = models.CharField(max_length=255, verbose_name=_("nome"))  # Required
    bio = models.CharField(max_length=360, blank=True, null=True, verbose_name=_("bio"))
    profile_picture = ResizedImageField(
        upload_to=profile_picture_path,
        size=[512, 512],
        quality=75,
        crop=['middle', 'center'],
        blank=True,
        null=True,
        verbose_name=_("foto de perfil")
    )

    is_active = models.BooleanField(default=True, verbose_name=_("ativo"))
    is_staff = models.BooleanField(default=False, verbose_name=_("staff"))

    EMAIl_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password']

    objects = UserManager()

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
