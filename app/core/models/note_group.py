import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class NoteGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    title = models.CharField(max_length=255,
                             verbose_name=_("título"),
                             help_text=_("Título do conjunto."))
    parent_folder = models.ForeignKey('Folder', null=True, blank=True, on_delete=models.CASCADE,
                                      verbose_name=_('pasta pai'),
                                      help_text=_('Pasta em que este conjunto se localiza'),
                                      related_name='note_groups',
                                      related_query_name='note_group')

    class Meta:
        verbose_name = _('conjunto de anotação')
        verbose_name_plural = _('conjunto de anotações')

    def __str__(self):
        return f'{self.parent_folder}/{self.title}'
