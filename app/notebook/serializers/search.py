from django.db.models import Q
from rest_framework import serializers

from core.models import Notebook, Folder, NoteGroup, Note
from notebook.serializers.folder import RelatedFolderSerializer
from notebook.serializers.note import RelatedNoteSerializer
from notebook.serializers.note_group import RelatedNoteGroupSerializer


class SearchResult:
    def __init__(self, notebook: Notebook, query):
        # Might require PostgreSQL to work properly
        self.folders = Folder.objects.filter(Q(notebook=notebook) & ~Q(parent_folder=None)).filter(
            title__icontains=query)
        self.note_groups = NoteGroup.objects.filter(parent_folder__notebook=notebook).filter(title__icontains=query)
        self.notes = Note.objects.filter(note_group__parent_folder__notebook=notebook).filter(title__icontains=query)


class SearchResultSerializer(serializers.Serializer):
    folders = RelatedFolderSerializer(many=True, read_only=True)
    note_groups = RelatedNoteGroupSerializer(many=True, read_only=True)
    note = RelatedNoteSerializer(many=True, read_only=True)
