import uuid

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Folder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    title = models.CharField(max_length=255,
                             verbose_name=_("título"),
                             help_text=_("Título da pasta."))
    notebook = models.ForeignKey('Notebook', on_delete=models.CASCADE, verbose_name=_('caderno'),
                                 help_text=_('Caderno onde a pasta se localiza.'),
                                 related_name='folders',
                                 related_query_name='folder'
                                 )

    parent_folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.CASCADE,
                                      verbose_name=_('pasta pai'),
                                      help_text=_('Pasta em que esta pasta se localiza, em caso de nulo, pasta raiz.'),
                                      related_name='sub_folders',
                                      related_query_name='sub_folder')

    class Meta:
        verbose_name = _('pasta')
        verbose_name_plural = _('pastas')
        constraints = [models.UniqueConstraint(fields=['notebook'], condition=Q(parent_folder=None),
                                               name='unique_parent_folder')]

    def __str__(self):
        return self.title
