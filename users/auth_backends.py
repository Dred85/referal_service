from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class EnterCodeBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        phone = kwargs.get("phone")
        enter_code = kwargs.get("password")

        if phone is None or enter_code is None:
            return None

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

        correct_enter_code = request.session.pop(phone, "")
        if enter_code == correct_enter_code:
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
