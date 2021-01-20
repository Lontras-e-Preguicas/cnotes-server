from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import User

CREATE_USER_URL = reverse('user:create')


class UserAPITests(TestCase):
    """Tests for the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """Test the creation of a valid user"""
        payload = {
            'email': 'ambrosia@rosie.tucker',
            'name': 'Ambrosia - Rosie Tucker',
            'bio': 'Ambrosia\'s turning me honest',
            'password': '17PBeLUldWC941sX8Ffmkd',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, 'User creation success')

        created_user = User.objects.get(email=res.data['email'])
        self.assertTrue(created_user.check_password(payload['password']), 'Assert if the password is usable')
        self.assertNotIn('password', res.data, 'Check if the returned data does not contain the password')

    def test_create_existing_user(self):
        """Test the creation of an invalid user"""
        payload = {
            'email': 'ambrosia@rosie.tucker',
            'name': 'Ambrosia - Rosie Tucker',
            'bio': 'Ambrosia\'s turning me honest',
            'password': '17PBeLUldWC941sX8Ffmkd',
        }

        User.objects.create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if error on creating existing user')

    def test_password_validation(self):
        """Test if the password is being properly validated"""
        payload = {
            'email': 'ambrosia@rosie.tucker',
            'name': 'Ambrosia - Rosie Tucker',
            'bio': 'Ambrosia\'s turning me honest',
            'password': 'passwd1',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if error on weak password')
