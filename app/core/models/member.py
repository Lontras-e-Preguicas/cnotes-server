import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4.")
                          )
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('usuário'),
                             help_text=_('Usuário membro de um caderno')
                             )
    notebook = models.ForeignKey('Notebook', on_delete=models.CASCADE, verbose_name=_('caderno'),
                                 help_text=_('Caderno no qual o usuário é membro'),
                                 )

    class Roles(models.TextChoices):
        MEMBER = 'member', _('Member')
        MODERATOR = 'mod', _('Moderator')
        ADMIN = 'admin', _('Administrator')

    role = models.CharField(max_length=6,
                            choices=Roles.choices,
                            default=Roles.MEMBER,
                            help_text=_("Papel desempenhado pelo membro dentro do caderno")
                            )

    member_since = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de entrada'),
                                        help_text=_('Data de entrada do membro no caderno')
                                        )
    is_active = models.BooleanField(default=True, verbose_name=_('ativo'),
                                    help_text=_('Indica se o membro está ativo')
                                    )
    is_banned = models.BooleanField(default=False, verbose_name=_('banido'),
                                    help_text=_('Indica se o membro está banido')
                                    )

    class Meta:
        verbose_name = _('membro')
        verbose_name_plural = _('membros')

    def __str__(self):
        return self.title
