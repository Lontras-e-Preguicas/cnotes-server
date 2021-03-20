import os
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


def attachment_file_path(instance, filename):
    ext = filename.split('.')[-1]
    new_filename = f'{instance.id}.{ext}'
    return os.path.join('attachments', new_filename)


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    note = models.ForeignKey('note', on_delete=models.CASCADE, verbose_name=_('anotação'),
                             help_text=_('Anotação onde o anexo se localiza.'),
                             related_name='attachments',
                             related_query_name='attachment')
    uploaded_file = models.FileField(
        upload_to=attachment_file_path,
        verbose_name=_('arquivo anexado'),
        help_text=_('O arquivo anexado.')
    )

    uploaded_at = models.DateTimeField(auto_now=True, verbose_name=_("enviada em"),
                                       help_text=_('Momento da última modificação no anexo.'))
