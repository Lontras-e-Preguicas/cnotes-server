from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notebook.views.note import NoteViewSet
from notebook.views.folder import FolderViewSet
from notebook.views.note_group import NoteGroupViewSet
from notebook.views.member import MemberViewSet

app_name = 'notebook'

main_router = DefaultRouter()

main_router.register('note', NoteViewSet, 'note')
main_router.register('folder', FolderViewSet, 'folder')
main_router.register('note_group', NoteGroupViewSet, 'note-group')
main_router.register('member', MemberViewSet, 'member')


urlpatterns = [
    path('', include(main_router.urls)),
]
