import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))

    note = models.ForeignKey('Note', on_delete=models.CASCADE, verbose_name=_('anotação'),
                             help_text=_('Anotação avaliada.'),
                             related_name='ratings', related_query_name='rating'
                             )

    rating = models.IntegerField(verbose_name=_('avaliação'),
                                 help_text=_('Valor da avaliação dada.'), )  # Adicionar validators

    rater = models.ForeignKey('Member', on_delete=models.CASCADE, verbose_name=_('avaliador'),
                              help_text=_('Autor da avaliação.'),
                              related_name='rates',
                              related_query_name='rate'
                              )

    rated_date = models.DateTimeField(auto_now=True, verbose_name=_("data da avaliação"),
                                      help_text=_("Data da avaliação."))

    class Meta:
        verbose_name = _('avaliação')
        verbose_name_plural = _('avaliações')
        unique_together = ('note', 'rater')

    def __str__(self):
        return f'{{{self.note}}}/{{{self.rater}}}: {self.rating}'
