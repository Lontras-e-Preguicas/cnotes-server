from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Notebook, NoteGroup, User

NOTE_GROUP_URL = reverse('notebook:note-group-list')


class PrivateNoteGroupAPITests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='test@mail.com', name="test user", password="test_password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.notebook = Notebook.objects.create_notebook(owner=self.user, title='Wow, it\'s a notebook')
        self.folder = self.notebook.root_folder
        self.note_groups = [NoteGroup.objects.create(parent_folder=self.folder, title=f'NoteGroup {i}') for i in
                            range(4)]

    def detail_url(self, id):
        return reverse('notebook:note-group-detail', args=[id])

    def test_note_group_creation(self):
        """Test the creation of a new note_group"""

        payload = {
            'parent_folder': self.folder.id,
            'title': 'New NoteGroup'
        }

        res = self.client.post(NOTE_GROUP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)
        new_id = res.data['id']
        created_note_group = NoteGroup.objects.get(id=new_id)  # Raises exception if not found

        self.assertEqual(created_note_group.title, payload['title'])
        self.assertEqual(created_note_group.parent_folder, self.folder)

        new_user = User.objects.create_user(email='new_user@test.io', name="Julião Tavares", password="thpquu8tqu8hgr")

        self.client.force_authenticate(new_user)

        res = self.client.post(NOTE_GROUP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_note_group_retrieval(self):
        """Test the retrieval of note_groups"""

        res = self.client.get(self.detail_url(self.note_groups[0].id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn('title', res.data)
        self.assertEqual(res.data['title'], self.note_groups[0].title)
