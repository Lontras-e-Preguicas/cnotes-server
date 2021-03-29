from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Note, Notebook, NoteGroup, Member, Folder, Comment

COMMENT_URL = reverse('notebook:comment-list')
UserModel = get_user_model()


def create_user_util(**fields):
    data = {
        'email': 'ambrosia@rosie.tucker',
        'name': 'Ambrosia - Rosie Tucker',
        'bio': 'Ambrosia\'s turning me honest',
        'password': '17PBeLUldWC941sX8Ffmkd',
        **fields
    }

    return UserModel.objects.create_user(**data)


class PrivateCommentApiTests(TestCase):
    """Private Comment API tests"""
    current_user: UserModel
    notebook: Notebook
    note_group: NoteGroup
    current_user_membership: Member
    folder: Folder
    note_group: NoteGroup
    note: Note

    def setUp(self):
        self.current_user = create_user_util()
        self.client = APIClient()
        self.client.force_authenticate(user=self.current_user)

        self.notebook = Notebook.objects.create_notebook(owner=self.current_user, title='Test Notebook')
        self.folder = Folder.objects.get(notebook=self.notebook, parent_folder=None)
        self.current_user_membership = Member.objects.get(notebook=self.notebook, user=self.current_user)
        self.note_group = NoteGroup.objects.create(parent_folder=self.folder, title='Test NoteGroup')
        self.note = Note.objects.create(note_group=self.note_group, author=self.current_user_membership)

    def detail_url(self, id):
        return reverse('notebook:comment-detail', args=[id])

    def test_comment(self):
        """AIO Comment API tests"""
        payload = {
            'note': self.note.id,
            'message': 'A test message, this is! Shall, you, read it.'
        }

        res = self.client.post(COMMENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        comments = Comment.objects.filter(note=self.note)
        self.assertEqual(comments.count(), 1)

        comment = comments.first()
        res = self.client.get(self.detail_url(comment.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.post(f'{COMMENT_URL}{comment.id}/solve/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertTrue(comment.solved)

        res = self.client.post(f'{COMMENT_URL}{comment.id}/unsolve/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertFalse(comment.solved)

        res = self.client.patch(self.detail_url(comment.id), {'message': 'new message.'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.message, 'new message.')
