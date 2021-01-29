from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model, tokens
from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
RESET_REQUEST_URL = reverse('user:password-reset-request')
RESET_CONFIRM_URL = reverse('user:password-reset-confirm')

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

    def test_password_validation_length(self):
        """Test if the password length is being properly validated"""
        payload = {
            **DEFAULT_PAYLOAD,
            'password': 'passwd1',
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if error on weak password')

    def test_common_password_validation(self):
        """Test if the password is in the common password database"""
        payload = {
            **DEFAULT_PAYLOAD,
            'password': 'password1'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if the password is common')

    def test_numeric_password_validation(self):
        """Test if the password contains letters"""
        payload = {
            **DEFAULT_PAYLOAD,
            'password': '5346726482374'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST, 'Check if the password is not entirely numeric')

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

    def test_me_authentication_required(self):
        """Test that user authentication is required for the me endpoint"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_request(self):
        """Test the password reset token request"""
        user = create_user_util()

        request_payload = {
            'email': user.email
        }

        # Non-existing account
        res = self.client.post(RESET_REQUEST_URL, {'email': 'not@registered'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)  # Leak safe
        self.assertEqual(len(mail.outbox), 0)

        # Existing account
        res = self.client.post(RESET_REQUEST_URL, request_payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox.pop()
        self.assertIn(str(user.id), str(email.message()))  # Check if UID is on the message

    def test_password_reset_confirm(self):
        """Test the password reset token confirm"""
        user = create_user_util()
        user_2 = create_user_util(email='test@test.com')

        token_generator = tokens.PasswordResetTokenGenerator()

        request_payload_valid = {
            'uid': str(user.id),
            'token': token_generator.make_token(user),
            'password': 'strong_password_122'
        }

        request_payload_invalid = {
            **request_payload_valid,
            'token': token_generator.make_token(user_2)
        }

        # Other user's token
        res = self.client.post(RESET_CONFIRM_URL, request_payload_invalid)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # Right token
        res = self.client.post(RESET_CONFIRM_URL, request_payload_valid)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.check_password(request_payload_valid['password']))


class PrivateUserAPITests(TestCase):
    """Tests for the User API that requires authentication"""

    def setUp(self):
        self.user = create_user_util()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_me_personal_data_retrieval(self):
        """Test that me is returning only the relevant personal data"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn('id', res.data, 'ID retrieval')

        self.assertEqual(res.data, {
            'id': res.data['id'],  # the id might be unpredictable
            'email': DEFAULT_PAYLOAD['email'],
            'name': DEFAULT_PAYLOAD['name'],
            'bio': DEFAULT_PAYLOAD['bio'],
            'profile_picture': None
        })

    def test_me_personal_data_update(self):
        """Test updating personal info"""
        payload = {
            'name': 'Rose Tucker: Ambrosia',
            'password': 'rosie tucker '  # Password with trailing space
        }

        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
