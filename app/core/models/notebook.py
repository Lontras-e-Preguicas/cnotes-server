import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from .folder import Folder
from .member import Member


class NotebookManager(models.Manager):
    def create_notebook(self, owner=None, **kwargs):
        notebook = self.create(owner=owner, **kwargs)
        Member.objects.create(user=owner, notebook=notebook, role=Member.Roles.ADMIN)  # Create owner as member
        Folder.objects.create(notebook=notebook, parent_folder=None, title='root')  # Create root folder
        return notebook


class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,
                          help_text=_("ID único seguindo o padrão UUID4."))
    title = models.CharField(max_length=255,
                             verbose_name=_("título"),
                             help_text=_("Título do caderno."))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_("data de criação"),
                                         help_text=_("Data de criação do caderno."))

    owner = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name=_('dono'),  # pain
                              help_text=_('Atual dono do caderno.'),
                              related_name='notebooks',
                              related_query_name='notebook'
                              )

    objects = NotebookManager()

    class Meta:
        verbose_name = _('caderno')
        verbose_name_plural = _('cadernos')

    @property
    def root_folder(self):
        return self.folders.get(parent_folder=None)

    @property
    def owner_as_member(self):
        return Member.objects.get(notebook=self, user=self.owner)

    def __str__(self):
        return self.title
