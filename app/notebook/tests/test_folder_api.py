from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Notebook, Folder, User

FOLDER_URL = reverse('notebook:folder-list')
NOTEBOOK_ROOT_FOLDER_URL = reverse('notebook:folder-root')


class PrivateFolderAPITests(TestCase):
    """Private Folder API Tests"""

    def setUp(self):
        self.user = User.objects.create_user(email='test@mail.com', name='Test User', password='test_password')
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.notebook = Notebook.objects.create_notebook(owner=self.user, title="Test Notebook")
        self.root_folder = Folder.objects.get(notebook=self.notebook, parent_folder=None)

    def detail_url(self, id):
        return reverse('notebook:folder-detail', args=[id])

    def test_folder_creation(self):
        """Test the creation of a folder"""
        test_folder_title = "Test Title"

        res = self.client.post(FOLDER_URL, {'notebook': self.notebook.id, 'title': test_folder_title})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        created_folder_id = res.data['id']

        new_folder = self.root_folder.sub_folders.get(id=created_folder_id)  # Raises exception if doesn't exist
        self.assertEqual(new_folder.title, test_folder_title)

        res = self.client.post(FOLDER_URL, {'parent_folder': new_folder.id, 'title': test_folder_title})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(new_folder.sub_folders.all()) == 1)

        res = self.client.post(FOLDER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_folder_retrieval(self):
        """Test folder listing"""

        res = self.client.get(self.detail_url(id=self.root_folder.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('sub_folders', res.data)
        self.assertTrue(isinstance(res.data['sub_folders'], list))

        res = self.client.get(NOTEBOOK_ROOT_FOLDER_URL + f"?notebook={self.notebook.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('sub_folders', res.data)
        self.assertTrue(isinstance(res.data['sub_folders'], list))
