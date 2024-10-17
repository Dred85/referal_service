from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class EnterCodeBackend(BaseBackend):
    """
    Кастомный backend для аутентификации пользователя по номеру телефона и коду подтверждения.
    """

    def authenticate(self, request, **kwargs):
        """
        Метод аутентификации пользователя по номеру телефона и коду подтверждения.

        :param request: HTTP запрос, содержащий сессию с кодом подтверждения.
        :param kwargs: Дополнительные аргументы, содержащие 'phone' и код подтверждения.
        :return: User объект, если аутентификация успешна, или None, если неуспешна.
        """
        phone = kwargs.get("phone")
        enter_code = kwargs.get("password")

        if phone is None or enter_code is None:
            return None

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        # Попытка извлечь код из сессии и сравнить его с введённым кодом
        correct_enter_code = request.session.pop(phone, "")
        if enter_code == correct_enter_code:
            return user
        return None

    def get_user(self, user_id):
        """
        Возвращает пользователя по его ID.

        :param user_id: ID пользователя, который нужно найти.
        :return: User объект, если пользователь существует, или None, если не существует.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

