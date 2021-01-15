from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email: str, name: str, password: str, bio: str = None, **extra_fields):
        if not email:
            raise ValueError(_('E-mail address is required'))
        if not name:
            raise ValueError(_('Name is required'))
        if not password:
            raise ValueError(_('Password is required'))

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, bio=bio, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user



class User(AbstractBaseUser):
    """User model, used for authentication"""
    email = models.EmailField(unique=True) # Required
    name = models.CharField(max_length=255) # Required
    bio = models.CharField(max_length=360)
    profile_picture = models.ImageField()

    EMAIl_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'email', 'password']

    objects = UserManager()
