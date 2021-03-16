import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    author = models.ForeignKey('Member', on_delete=models.CASCADE, verbose_name=_('autor'),
                               help_text=_('Autor da anotação.'),
                               related_name='notes',
                               related_query_name='note'
                               )
    note_group = models.ForeignKey('NoteGroup', on_delete=models.CASCADE, verbose_name=_('conjunto de anotações'),
                                   help_text=_('Conjunto de anotações onde a anotação está contida.'),
                                   related_name='notes',
                                   related_query_name='note'
                                   )
    title = models.CharField(max_length=255, blank=False, verbose_name=_("título"), help_text=_('Título da anotação.'))

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("data de criação"),
                                         help_text=_("Data de criação da anotação."))

    content = models.TextField(verbose_name=_('conteúdo'), help_text=_('Conteúdo da anotação.'), blank=True)

    last_edited = models.DateTimeField(auto_now=True, verbose_name=_("momento da última edição"),
                                       help_text=_("Indica o momento da última edição."))

    last_edited_by = models.ForeignKey('Member', on_delete=models.SET_NULL, null=True, default=None,
                                       verbose_name=_('última edição por'),
                                       help_text=_("Indica quem realizou a última edição."))

    class Meta:
        verbose_name = _('anotação')
        verbose_name_plural = _('anotações')

    @property
    def notebook(self):
        return self.note_group.notebook

    @property
    def avg_rating(self):
        return self.ratings.aggregate(models.Avg('rating'))['rating__avg']

    def __str__(self):
        return self.title
