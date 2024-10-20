from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserPhoneSerializer(serializers.ModelSerializer):
    """Сериализатор для номера телефона пользователя"""

    phone = serializers.CharField()

    def validate_phone(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError(
                "Номер телефона должен состоять из 11 цифр."
            )
        return value

    class Meta:
        model = User
        fields = ["phone"]


class UserRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных пользователя"""

    referrals = serializers.SerializerMethodField()
    invited_by_phone = serializers.SerializerMethodField()
    invite_code_referer = serializers.SerializerMethodField()

    def get_referrals(self, obj):
        """Метод получает объект пользователя (obj) и возвращает список номеров телефонов пользователей,
        которые являются его рефералами."""
        return obj.referrals.values_list("phone", flat=True)

    def get_invited_by_phone(self, obj):
        """Этот метод проверяет, есть ли у пользователя invited_by (т.е. реферер).
        Если реферер есть, он возвращает его номер телефона. Если реферера нет, возвращается "У Вас нет реферера".
        """
        referrer = obj.invited_by
        if referrer:
            return f"+{referrer.phone}"  # Возвращаем номер телефона реферера
        return "У Вас нет реферера"

    def get_invite_code_referer(self, obj):
        """Этот метод проверяет, есть ли у пользователя invited_by (т.е. реферер).
        Если реферер есть, он возвращает его invite_code. Если реферера нет, возвращается "У Вас нет кода от реферера".
        """
        referrer = obj.invited_by
        if referrer:
            return referrer.invite_code  # Возвращаем код реферера
        return "У Вас нет кода от реферера"

    class Meta:
        model = User
        fields = [
            "phone",
            "referrals",
            "invite_code",
            "invited_by_phone",
            "invite_code_referer",
        ]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # добавление номера телефона в payload
        token["phone"] = user.phone
        return token
