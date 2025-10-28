from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

class AccountsSmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login(self):
        url = reverse('accounts-register')
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "ComplexPass!234",
            "password2": "ComplexPass!234",
            "role": "sme"
        }
        r = self.client.post(url, data, format='json')
        self.assertEqual(r.status_code, 201)
        token_url = reverse('accounts-token-obtain')
        r2 = self.client.post(token_url, {"username": "testuser", "password": "ComplexPass!234"}, format='json')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('access', r2.data)
