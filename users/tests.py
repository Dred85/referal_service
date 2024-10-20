from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class AuthTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(phone="70000000000")
        self.client.force_authenticate(user=self.user)

    def test_get_code(self):
        """
        Проверяет отправку кода для нового номера телефона и
        повторную отправку кода для уже зарегистрированного номера.
        """
        url = reverse("users:get_code")

        # Тестируем отправку кода для нового номера
        response = self.client.post(url, data={"phone": "70000000001"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Тестируем повторную отправку кода для того же номера
        response = self.client.post(url, data={"phone": "70000000001"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_referrer(self):
        """
        Проверяет установку реферала по инвайт-коду.
        Сначала тестируется случай с невалидным кодом, затем с валидным.
        """
        url = reverse("users:set_referrer")
        self.client.post(reverse("users:get_code"), data={"phone": "70000000001"})
        invite_code = User.objects.get(phone="70000000001").invite_code

        # Проверяем, что неверный код возвращает 404
        response = self.client.post(url, data={"invite_code": "hhhhhh"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Проверяем установку реферала с валидным кодом
        response = self.client.post(url, data={"invite_code": invite_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve(self):
        """
        Проверяет получение информации о пользователе.
        Убедимся, что возвращается правильный номер телефона.
        """
        url = reverse("users:retrieve")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_backend(self):
        """
        Проверяет отправку кода с неверными учетными данными.
        Ожидаем статус 401 Unauthorized.
        """
        url = reverse("users:send_code")
        response = self.client.post(
            url, data={"phone": "70000000000", "password": "1234"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_send_code_with_invalid_phone(self):
        """
        Проверяет отправку кода с невалидным номером телефона.
        Ожидаем статус 400 Bad Request.
        """
        url = reverse("users:send_code")
        response = self.client.post(url, data={"phone": "invalid_phone"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_referrer_when_already_set(self):
        """
        Проверяет установку реферала, когда он уже установлен.
        Ожидаем статус 400 Bad Request при повторной попытке.
        """
        url = reverse("users:set_referrer")
        self.client.post(reverse("users:get_code"), data={"phone": "70000000001"})
        invite_code = User.objects.get(phone="70000000001").invite_code

        # Устанавливаем реферала
        self.client.post(url, data={"invite_code": invite_code})
        # Пытаемся установить его снова
        response = self.client.post(url, data={"invite_code": invite_code})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_retrieve_with_unauthenticated_user(self):
        """
        Проверяет получение информации о пользователе для неаутентифицированного пользователя.
        Ожидаем статус 401 Unauthorized.
        """
        url = reverse("users:retrieve")
        self.client.logout()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_auth_backend_with_invalid_credentials(self):
        """
        Проверяет отправку кода с неверным паролем.
        Ожидаем статус 401 Unauthorized.
        """
        url = reverse("users:send_code")
        response = self.client.post(
            url, data={"phone": "70000000000", "password": "wrong_password"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_set_referrer_with_invalid_code(self):
        """
        Проверяет установку реферала с невалидным инвайт-кодом.
        Ожидаем статус 400 Bad Request для пустого кода и 404 Not Found для неверного кода.
        """
        url = reverse(
            "users:set_referrer"
        )  # Убедитесь, что вы используете правильный URL
        response = self.client.post(url, data={"invite_code": ""})  # Пустой инвайт-код
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

        response = self.client.post(url, data={"invite_code": "invalid_code"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
