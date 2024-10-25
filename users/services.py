import string
from pprint import pprint
from random import choice
from time import sleep

from django.contrib.auth import get_user_model
from smsaero import SmsAero, SmsAeroException

from config.settings import SMSAERO_API_KEY, SMSAERO_EMAIL

User = get_user_model()


def send_sms(phone: int, message: str) -> dict:
    """
    Отправка смс на номер телефона через службу SMS Aero

    Parameters:
    phone (int): The phone number to which the SMS message will be sent.
    message (str): The content of the SMS message to be sent.

    Returns:
    dict: A dictionary containing the response from the SmsAero API.
    """
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    return api.send_sms(phone, message)


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


def send_enter_code(phone: object, code: object) -> object:
    print(f"Номер телефона: {phone}  код для авторизации: {code}")
    # Преобразуем наш номер из строки в int
    phone = int(phone)
    try:
        "Реально отправляем смс с кодом из 4 цифр на реальный номер"
        result = send_sms(phone, code)
        pprint(result)
        print(f"phone: {phone} | code: {code}")

    except SmsAeroException as e:
        print(f"Произошла ошибка: {e}")
    sleep(2)
