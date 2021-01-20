from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')

DEFAULT_PAYLOAD = {
            'email': 'ambrosia@rosie.tucker',
            'name': 'Ambrosia - Rosie Tucker',
            'bio': 'Ambrosia\'s turning me honest',
            'password': '17PBeLUldWC941sX8Ffmkd',
        }


def create_user_util(**fields):
    data = {
        **DEFAULT_PAYLOAD,
        **fields
    }

    return get_user_model().objects.create_user(**data)


class PublicUserAPITests(TestCase):
    """Tests for the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """Test the creation of a valid user"""
        payload = DEFAULT_PAYLOAD

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, 'get_user_model() creation success')

        created_user = get_user_model().objects.get(email=res.data['email'])
        self.assertTrue(created_user.check_password(payload['password']), 'Assert if the password is usable')
        self.assertNotIn('password', res.data, 'Check if the returned data does not contain the password')

    def test_create_existing_user(self):
        """Test the creation of an invalid user"""
        payload = DEFAULT_PAYLOAD

        create_user_util(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if error on creating existing user')

    def test_password_validation(self):
        """Test if the password is being properly validated"""
        payload = {
            **DEFAULT_PAYLOAD,
            'password': 'passwd1',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if error on weak password')

    def test_token_creation_successful(self):
        """Test the successful creation of an authentication token"""
        payload = DEFAULT_PAYLOAD

        create_user_util(**payload)

        res = self.client.post(TOKEN_URL, {'email': payload['email'], 'password': payload['password']})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_token_creation_bad_credentials(self):
        """Test the failure of generating a token with bad credentials"""
        payload = DEFAULT_PAYLOAD

        create_user_util(**payload)

        res = self.client.post(TOKEN_URL, {'email': payload['email'], 'password': 'password'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_creation_missing_fields(self):
        """Test the authentication failure with missing fields"""
        payload = DEFAULT_PAYLOAD

        create_user_util(**payload)

        res = self.client.post(TOKEN_URL, {'email': payload['email']})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
