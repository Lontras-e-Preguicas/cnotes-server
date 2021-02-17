import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Invite(models.Model):
    # id: int,
    # sender: Member,
    # receiver: User,
    # invite_date: datetime
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4.")
                          )
    sender = models.ForeignKey('Member', on_delete=models.CASCADE, verbose_name=_('remetente'),
                               help_text=_('Usuário remetente do convite'),
                               related_name='invites_sent',
                               related_query_name='invite_sent'
                               )
    receiver = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('destinatário'),
                                 help_text=_('Usuário destinatário do convite'),
                                 related_name='invites',
                                 related_query_name='invite'
                                 )
    invite_date = models.DateTimeField(auto_now_add=True, verbose_name=_('data do convite'),
                                       help_text=_('Data do envio do convite para um usuário')
                                       )

    class Meta:
        verbose_name = _('convite')
        verbose_name_plural = _('convites')

    def __str__(self):
        return self.title
