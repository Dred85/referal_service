from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class AuthTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(phone='70000000000')
        self.client.force_authenticate(user=self.user)

    def test_get_code(self):
        """
        Тест проверяет логику получения кода.
        Сначала отправляется запрос на получение кода для нового номера телефона, что возвращает статус 201 (Created).
        Затем повторный запрос с тем же номером телефона возвращает статус 200 (OK).
        """
        url = reverse("users:get_code")
        response = self.client.post(url, data={'phone': '70000000001'})
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )
        response = self.client.post(url, data={'phone': '70000000001'})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

    def test_set_referrer(self):
        """
        Тест проверяет установку реферера (приглашённого пользователя).
        Отправляется некорректный код приглашения, что возвращает статус 404 (Not Found).
        Затем тест проверяет успешное использование правильного invite_code, который возвращает статус 200 (OK).
        """
        url = reverse("users:set_referrer")
        self.client.post(reverse("users:get_code"), data={'phone': '70000000001'})
        invite_code = User.objects.get(phone='+7000000001').invite_code
        response = self.client.post(url, data={'invite_code': 'badcod'})
        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )

        response = self.client.post(url, data={'invite_code': invite_code})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )

    def test_retrieve(self):
        """
        Тест проверяет получение профиля текущего пользователя.
        Отправляется GET-запрос на конечную точку retrieve, который возвращает статус 200 (OK)
        и проверяется, что возвращённый номер телефона соответствует пользователю, который был аутентифицирован.
        """
        url = reverse("users:retrieve")
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data.get('phone'), '70000000000'
        )

    def test_auth_backend(self):
        """
        Тест проверяет авторизацию пользователя.
        Отправляется POST-запрос на конечную точку send_code с неверным паролем, что возвращает статус 401 (Unauthorized).
        """
        url = reverse("users:send_code")
        response = self.client.post(url, data={'phone': '70000000000', 'password': '1234'})
        self.assertEqual(
            response.status_code, status.HTTP_401_UNAUTHORIZED
        )
