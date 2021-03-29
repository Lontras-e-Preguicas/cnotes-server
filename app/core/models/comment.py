import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))

    note = models.ForeignKey('Note', on_delete=models.CASCADE, verbose_name=_('anotação'),
                             help_text=_('Anotação comentada.'),
                             related_name='comments', related_query_name='comment',
                             )

    commenter = models.ForeignKey('Member', on_delete=models.CASCADE, verbose_name=_('comentarista'),
                                  help_text=_('Autor do comentário.'),
                                  related_name='comments',
                                  related_query_name='comment',
                                  )

    message = models.CharField(max_length=1023, verbose_name=_('mensagem'), help_text=_('Conteúdo do comentário.'))

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("data de criação"),
                                         help_text=_("Data de criação do comentário."))

    solved = models.BooleanField(default=False, verbose_name=_('resolvido'),
                                 help_text=_('Indicativo de que o comentário já foi resolvido'))

    class Meta:
        verbose_name = _('comentário')
        verbose_name_plural = _('comentários')

    def __str__(self):
        return f'[{self.creation_date}] {{{self.note}}}/{{{self.commenter}}}'
