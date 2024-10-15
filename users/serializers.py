from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()


class UserPhoneSerializer(serializers.ModelSerializer):
    """Сериализатор для номера телефона пользователя"""
    phone = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'phone'
        ]


class UserRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных пользователя"""
    referrals = serializers.SerializerMethodField()
    invited_by_code = serializers.SerializerMethodField()

    def get_referrals(self, obj):
        return obj.referrals.values_list('phone', flat=True)

    def get_invited_by_code(self, obj):
        referrer = obj.invited_by
        if referrer:
            return referrer.invite_code
        return None

    class Meta:
        model = User
        fields = ['phone', 'referrals', 'invite_code', 'invited_by_code']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)

        # добавление номера телефона в payload
        token['phone'] = user.phone
        return token
