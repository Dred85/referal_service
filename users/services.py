import string
from random import choice
from time import sleep

from django.contrib.auth import get_user_model

User = get_user_model()


def create_invite_code():
    """Создание инвайт-кода для реферальной системы, который состоит из 6 случайных цифр/букв"""
    existing_codes = User.objects.values_list("invite_code", flat=True)
    alphabet = string.ascii_letters + string.digits
    while True:
        code = ""
        for _ in range(6):
            code += choice(alphabet)
        if code not in existing_codes:
            break
    return code


def create_enter_code():
    """Создает код для входа в систему, который состоит из 4 случайных цифр"""
    code = ""
    for _ in range(4):
        code += choice(string.digits)
    return code


def send_enter_code(phone, code):
    print(f"phone: {phone} | code: {code}")
    sleep(2)
