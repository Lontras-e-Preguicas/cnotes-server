import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    title = models.CharField(max_length=255,
                             verbose_name=_("título"),
                             help_text=_("Título do caderno."))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("data de criação"),
                                         help_text=_("Data de criação do caderno."))

    owner = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('dono'),  # pain
                              help_text=_('Atual dono do caderno.'))

    class Meta:
        verbose_name = _('caderno')
        verbose_name_plural = _('cadernos')

    def __str__(self):
        return self.title
