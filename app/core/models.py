from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str, bio: str = None, **extra_fields):
        """Create an user from its fields"""
        if not email:
            raise ValueError(_('Endereço de e-mail é obrigatório'))
        if not name:
            raise ValueError(_('Nome é obrigatório'))
        if not password:
            raise ValueError(_('Senha é obrigatória'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, bio=bio, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    """User model, used for authentication"""
    email = models.EmailField(unique=True)  # Required
    name = models.CharField(max_length=255)  # Required
    bio = models.CharField(max_length=360, null=True)
    profile_picture = models.ImageField(null=True)

    EMAIl_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password']

    objects = UserManager()
