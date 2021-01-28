from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
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


class User(AbstractBaseUser):
    """User model, used for authentication"""
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

    EMAIl_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password']

    objects = UserManager()

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
