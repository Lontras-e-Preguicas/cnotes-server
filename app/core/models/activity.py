import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Activity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4.")
                          )
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('usuário'),
                             help_text=_('Usuário que verá suas atividades'),
                             related_name='activities',
                             related_query_name='activity'
                             )
    title = models.CharField(max_length=255, verbose_name=_('título'),
                             help_text=_('Título da atividade')
                             )
    description = models.CharField(max_length=255, verbose_name=_('descrição'),
                                   help_text=_('Descrição da atividade')
                                   )
    seen = models.BooleanField(default=False, verbose_name=_('visto'),
                                    help_text=_('Indica se a atividade foi vista')
                                    )

    class Meta:
        verbose_name = _('atividade')
        verbose_name_plural = _('atividades')

    def __str__(self):
        return self.title
