from django.contrib.auth import get_user_model
from rest_framework import generics, status, views
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import MyTokenObtainPairSerializer, UserPhoneSerializer, UserRetrieveSerializer
from users.services import create_enter_code, create_invite_code, send_enter_code

User = get_user_model()

class GetOrCreateModelMixin:
    """
    Миксин для обработки создания или получения объекта модели.
    """

    def get_or_create(self, request, *args, **kwargs):
        """
        Получает или создает объект модели на основе данных запроса.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с сериализованными данными
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = self.perform_get_or_create(serializer)
        if created:
            headers = self.get_success_headers(request.data)
            return Response(
                {"serializer": serializer},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response({"serializer": serializer}, status=status.HTTP_200_OK)

    def perform_get_or_create(self, serializer):
        """
        Выполняет логику создания или получения объекта.
        Должен быть переопределен в наследующих классах.

        :param serializer: Сериализатор с валидированными данными
        :raises NotImplementedError: Если метод не переопределен
        """
        raise NotImplementedError

    def get_success_headers(self, data):
        """
        Возвращает заголовки для успешного ответа.

        :param data: Данные ответа
        :return: Заголовки ответа
        """
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос, получая или создавая объект.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с результатом
        """
        return self.get_or_create(request, *args, **kwargs)


class UserGetEnterCodeMixin(GetOrCreateModelMixin):
    model = User
    serializer_class = UserPhoneSerializer

    def perform_get_or_create(self, serializer):
        user, created = self.model.objects.get_or_create(**serializer.validated_data,
                                                         defaults={"invite_code": create_invite_code()})
        enter_code = create_enter_code()
        self.request.session[user.phone] = enter_code
        send_enter_code(user.phone, enter_code)

        return created


class UserGetCodeAPIView(UserGetEnterCodeMixin, generics.GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'get_code.html'

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class()
        return Response({'serializer': serializer})


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения токена по номеру телефона.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "send_code.html"
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для получения токена.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с токеном или ошибками
        """
        serializer = self.serializer_class()
        print(
            *[
                f"{k}: {v}"
                for k, v in super().post(request, *args, **kwargs).data.items()
            ],
            sep="\n",
        )
        return Response({"serializer": serializer})

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая форму для получения токена.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с формой
        """
        serializer = self.serializer_class()
        return Response({"serializer": serializer})


class MyTokenRefreshView(TokenRefreshView):
    """
    Представление для обновления токена.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "refresh.html"
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос для обновления токена.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с новым токеном или ошибками
        """
        serializer = self.get_serializer_class()()
        print(
            *[
                f"{k}: {v}"
                for k, v in super().post(request, *args, **kwargs).data.items()
            ],
            sep="\n",
        )
        return Response({"serializer": serializer})

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая форму для обновления токена.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с формой
        """
        serializer = self.get_serializer_class()()
        return Response({"serializer": serializer})


class SetReferrerAPIView(views.APIView):
    """
    Представление для установки реферала по инвайт-коду.
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "set_referrer.html"

    def post(self, request):
        """
        Обрабатывает POST-запрос для установки реферала.

        :param request: Запрос от клиента
        :return: Response с результатом установки реферала
        """
        invite_code = request.data.get("invite_code", "")
        referral = request.user
        if referral.invite_code == invite_code:
            return Response({"message": "Вы не можете ввести свой собственный инвайт-код"})
        if referral.invited_by is not None:
            return Response(
                {
                    "message": f"Вы уже являетесь рефералом пользователя с инвайт-кодом {referral.invited_by.invite_code}"
                }
            )

        referer = get_object_or_404(User.objects.filter(invite_code=invite_code))

        referral.invited_by = referer
        referral.save()
        return Response(
            {
                "message": f"Вы стали рефералом пользователя с инвайт-кодом {referer.invite_code}"
            }
        )

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая информацию о реферале.

        :param request: Запрос от клиента
        :return: Response с информацией о реферале
        """
        return Response()


class UserRetrieveAPIView(generics.RetrieveAPIView):
    """
    Представление для получения профиля пользователя.
    """

    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "retrieve.html"

    def get_object(self):
        """
        Возвращает текущего пользователя.

        :return: Текущий пользователь
        """
        return self.request.user