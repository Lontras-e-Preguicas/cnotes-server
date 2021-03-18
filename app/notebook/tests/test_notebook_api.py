from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import Notebook, Member, User

NOTEBOOK_URL = reverse('notebook:notebook-list')


class PrivateNotebookApiTests(TestCase):

    def setUp(self):
        self.current_user = User.objects.create_user(email='rip@life.io', name='Rest in Peace', password='test_rip')
        self.client = APIClient()
        self.client.force_authenticate(self.current_user)

    def detail_url(self, id, action='detail'):
        return reverse(f'notebook:notebook-{action}', args=[id])

    def test_notebook(self):
        payload = {
            'title': 'OOOOOOOOOF'
        }

        res = self.client.post(NOTEBOOK_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', res.data)

        notebook = Notebook.objects.get(id=res.data['id'])
        membership = notebook.members.get(user=self.current_user)
        self.assertEqual(membership.role, Member.Roles.ADMIN)
        notebook.root_folder

        res = self.client.get(NOTEBOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 1)

        res = self.client.get(self.detail_url(notebook.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('title', res.data)

        res = self.client.get(self.detail_url(notebook.id, 'root'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        res = self.client.get(self.detail_url(notebook.id, 'members'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(res.data, list))
        self.assertEqual(len(res.data), 1)

        res = self.client.get(self.detail_url(notebook.id, 'search') + '?q=kekekw')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('folders', res.data)
        self.assertIn('note_groups', res.data)
        self.assertIn('notes', res.data)

        res = self.client.patch(self.detail_url(notebook.id), {'title': 'UwU'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        notebook.refresh_from_db()
        self.assertEqual(notebook.title, 'UwU')
