from django.urls import path, include
from rest_framework.routers import DefaultRouter

from notebook.views.note import NoteViewSet
from notebook.views.folder import FolderViewSet

app_name = 'notebook'

main_router = DefaultRouter()

main_router.register('note', NoteViewSet, 'note')
main_router.register('folder', FolderViewSet, 'folder')

urlpatterns = [
    path('', include(main_router.urls)),
]
