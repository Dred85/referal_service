from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class AuthTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(phone="+7000000000")
        self.client.force_authenticate(user=self.user)

    def test_get_code(self):
        url = reverse("users:get_code")
        response = self.client.post(url, data={"phone": "+7000000001"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data={"phone": "+7000000001"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_referrer(self):
        url = reverse("users:set_referrer")
        self.client.post(reverse("users:get_code"), data={"phone": "+7000000001"})
        invite_code = User.objects.get(phone="+7000000001").invite_code
        response = self.client.post(url, data={"invite_code": "hhhhhh"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.post(url, data={"invite_code": invite_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        url = reverse("users:retrieve")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("phone"), "+7000000000")

    def test_auth_backend(self):
        url = reverse("users:send_code")
        response = self.client.post(
            url, data={"phone": "+7000000000", "password": "1234"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
