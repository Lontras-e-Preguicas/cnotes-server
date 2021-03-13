from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Note, Notebook, NoteGroup, Member, Folder

# Constants

NOTE_URL = reverse('notebook:note-list')
UserModel = get_user_model()


# Utils

def create_user_util(**fields):
    data = {
        'email': 'ambrosia@rosie.tucker',
        'name': 'Ambrosia - Rosie Tucker',
        'bio': 'Ambrosia\'s turning me honest',
        'password': '17PBeLUldWC941sX8Ffmkd',
        **fields
    }

    return UserModel.objects.create_user(**data)


class PrivateNoteApiTests(TestCase):
    """Private Note API tests"""
    current_user: UserModel
    notebook: Notebook
    note_group: NoteGroup
    current_user_membership: Member
    folder: Folder
    note_group: NoteGroup

    def setUp(self):
        self.current_user = create_user_util()
        self.client = APIClient()
        self.client.force_authenticate(user=self.current_user)

        self.notebook = Notebook.objects.create_notebook(owner=self.current_user, title='Test Notebook')
        self.folder = Folder.objects.get(notebook=self.notebook, parent_folder=None)
        self.current_user_membership = Member.objects.get(notebook=self.notebook, user=self.current_user)
        self.note_group = NoteGroup.objects.create(parent_folder=self.folder, title='Test NoteGroup')

    def detail_url(self, id):
        return reverse('notebook:note-detail', args=[id])

    def test_note_creation_success(self):
        """Test note creation with valid data"""
        payload = {
            'note_group': str(self.note_group.id),
            'title': 'test note'
        }

        res = self.client.post(NOTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_note = Note.objects.get(id=res.data['id'])
        self.assertEqual(created_note.title, payload['title'])
        self.assertEqual(created_note.note_group, self.note_group)

    def test_note_creation_failure(self):
        """Test note creation failure"""
        payload = {
            'note_group': str(self.note_group.id),
            'title': 'test note'
        }

        res = self.client.post(NOTE_URL, {'title': 'no notegroup'})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        res = self.client.post(NOTE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        other_user = create_user_util(email='test@mail.com', name='Ruby')
        self.client.force_authenticate(user=other_user)
        res = self.client.post(NOTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_note_update(self):
        """Test note update"""
        other_user = create_user_util(email='kekw@kekw.kek')
        other_user_membership = Member.objects.create(notebook=self.notebook, user=other_user)
        owner_test_note = Note.objects.create(note_group=self.note_group, author=self.current_user_membership)
        other_test_note = Note.objects.create(note_group=self.note_group, author=other_user_membership)
        other_notebook = Notebook.objects.create_notebook(owner=other_user, title='Other Notebook')
        other_note_group = NoteGroup.objects.create(title="Other NoteGroup", parent_folder=other_notebook.root_folder)

        # Change own note
        res = self.client.patch(self.detail_url(owner_test_note.id), {'title': 'New Title'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        owner_test_note.refresh_from_db()
        self.assertEqual(owner_test_note.title, 'New Title')

        # Change other users note
        res = self.client.patch(self.detail_url(other_test_note.id), {'title': 'New Title'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_test_note.refresh_from_db()
        self.assertEqual(other_test_note.title, 'New Title')

        # Move note between notebooks
        res = self.client.patch(self.detail_url(owner_test_note.id), {'note_group': str(other_note_group.id)})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.force_authenticate(other_user)

        # Change own note as member
        res = self.client.patch(self.detail_url(other_test_note.id), {'title': 'The New Title'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        other_test_note.refresh_from_db()
        self.assertEqual(other_test_note.title, 'The New Title')

        other_user_membership.is_active = False
        other_user_membership.save()

        # Access own note from a notebook that you are not in
        res = self.client.patch(self.detail_url(other_test_note.id), {'title': 'The New Title'})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        other_user_membership.is_active = True
        other_user_membership.is_banned = True
        other_user_membership.save()

        # Modify note while banned
        res = self.client.patch(self.detail_url(other_test_note.id), {'title': 'The New Title'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_note_destroy(self):
        """Test note destroy"""
        other_user = create_user_util(email='kekw@kekw.kek')
        other_user_membership = Member.objects.create(notebook=self.notebook, user=other_user)
        owner_test_note = Note.objects.create(note_group=self.note_group, author=self.current_user_membership)
        other_test_note = Note.objects.create(note_group=self.note_group, author=other_user_membership)

        # Delete own note
        res = self.client.delete(self.detail_url(owner_test_note.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Note.DoesNotExist):
            owner_test_note.refresh_from_db()

        self.client.force_authenticate(other_user)

        other_user_membership.is_active = False
        other_user_membership.save()

        # Delete own note from a notebook that you are not in
        res = self.client.delete(self.detail_url(other_test_note.id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

        other_user_membership.is_active = True
        other_user_membership.is_banned = True
        other_user_membership.save()

        # Delete note while banned
        res = self.client.delete(self.detail_url(other_test_note.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_note_retrieve(self):
        """Test note retrieval"""
        other_user = create_user_util(email='kekw@kekw.kek')

        Note.objects.create(note_group=self.note_group, author=self.current_user_membership)
        Note.objects.create(note_group=self.note_group, author=self.current_user_membership)
        Note.objects.create(note_group=self.note_group, author=self.current_user_membership)
        Note.objects.create(note_group=self.note_group, author=self.current_user_membership)

        # Get notes
        res = self.client.get(NOTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 4)

        # Get notes as new user
        self.client.force_authenticate(other_user)

        res = self.client.get(NOTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

        # Join existing notebook
        Member.objects.create(notebook=self.notebook, user=other_user)

        res = self.client.get(NOTE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 4)
