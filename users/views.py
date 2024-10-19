from django.contrib.auth import get_user_model
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.serializers import (MyTokenObtainPairSerializer,
                               UserPhoneSerializer, UserRetrieveSerializer)
from users.services import (create_enter_code, create_invite_code,
                            send_enter_code)

User = get_user_model()


class GetOrCreateModelMixin:
    """
    Миксин для обработки создания или получения объекта модели.
    """

    def perform_get_or_create(self, serializer):
        """
        Выполняет логику создания или получения объекта. Требуется переопределить.
        """
        raise NotImplementedError

    def get_or_create(self, request, *args, **kwargs):
        """
        Получает или создает объект модели на основе данных запроса.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created = self.perform_get_or_create(serializer)

        if created:
            headers = self.get_success_headers(serializer.validated_data)
            return Response(
                {"serializer": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response({"serializer": serializer.data}, status=status.HTTP_200_OK)

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
    """Миксин для получения или создания кода входа для пользователя."""

    model = User
    serializer_class = UserPhoneSerializer

    def perform_get_or_create(self, serializer):
        """Метод пытается получить существующего пользователя или создать нового, если такого нет."""
        user, created = self.model.objects.get_or_create(
            **serializer.validated_data, defaults={"invite_code": create_invite_code()}
        )
        enter_code = create_enter_code()
        self.request.session[user.phone] = enter_code
        send_enter_code(user.phone, enter_code)
        return created


class UserGetCodeAPIView(UserGetEnterCodeMixin, generics.GenericAPIView):
    """
    APIView для получения и отправки кода для авторизации на указанный номер телефона.
    Возвращает либо JSON, либо HTML в зависимости от заголовков запроса.
    """

    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "get_code.html"

    def get(self, request, *args, **kwargs):
        """
        Возвращает форму для ввода номера телефона и получения кода.
        """
        serializer = self.serializer_class()

        # Проверяем, что рендер используется для HTML
        if request.accepted_renderer.format == 'html':
            return Response({"serializer": serializer}, template_name=self.template_name)
        # Возвращаем данные в формате JSON
        return Response({"serializer": serializer.data})

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            created = self.perform_get_or_create(serializer)
            message = "На указанный номер телефона выслан код для авторизации."

            if created:
                if request.accepted_renderer.format == 'html':
                    return Response(
                        {"serializer": serializer, "message": message},
                        status=status.HTTP_201_CREATED,
                        template_name=self.template_name,
                    )
                return Response(
                    {"serializer": serializer.data, "message": message},
                    status=status.HTTP_201_CREATED,
                )

            if request.accepted_renderer.format == 'html':
                message = "Код отправлен повторно."
                return Response(
                    {"serializer": serializer, "message": message},
                    status=status.HTTP_200_OK,
                    template_name=self.template_name,
                )
            return Response(
                {"serializer": serializer.data, "message": "Код отправлен повторно."},
                status=status.HTTP_200_OK,
            )

        # Если данные невалидны, возвращаем ошибку
        if request.accepted_renderer.format == 'html':
            return Response({"serializer": serializer}, status=status.HTTP_400_BAD_REQUEST,
                            template_name=self.template_name)
        return Response({"serializer": serializer.data}, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Представление для получения токенов по номеру телефона.
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

    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
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
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            token_data = serializer.validated_data

            # Печать токенов для дебага (можно удалить позже)
            print(
                *[
                    f"{k}: {v}"
                    for k, v in token_data.items()
                ],
                sep="\n",
            )

            # Возвращаем JSON или HTML в зависимости от заголовка Accept
            if request.accepted_renderer.format == 'html':
                return Response(
                    {"serializer": serializer, "token_data": token_data},
                    template_name=self.template_name,
                    status=status.HTTP_200_OK
                )
            return Response(token_data, status=status.HTTP_200_OK)

        # Если данные невалидны, возвращаем ошибки в формате JSON или HTML
        if request.accepted_renderer.format == 'html':
            return Response(
                {"serializer": serializer, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
                template_name=self.template_name
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая форму для обновления токена.

        :param request: Запрос от клиента
        :param args: Дополнительные аргументы
        :param kwargs: Дополнительные ключевые аргументы
        :return: Response с формой
        """
        serializer = self.get_serializer_class()()
        return Response({"serializer": serializer}, template_name=self.template_name)

class SetReferrerAPIView(views.APIView):
    """
    Представление для установки реферала по инвайт-коду.
    """

    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = "set_referrer.html"

    def post(self, request):
        """
        Обрабатывает POST-запрос для установки реферала.
        :param request: Запрос от клиента
        :return: Response с результатом установки реферала
        """
        invite_code = request.data.get("invite_code", "")
        referral = request.user

        if not invite_code:
            error_message = "Инвайт-код не может быть пустым"
            return self._build_response({"error": error_message}, status.HTTP_400_BAD_REQUEST)

        if referral.invite_code == invite_code:
            error_message = "Вы не можете ввести свой собственный инвайт-код"
            return self._build_response({"message": error_message}, status.HTTP_400_BAD_REQUEST)

        if referral.invited_by is not None:
            error_message = f"Вы уже являетесь рефералом пользователя с инвайт-кодом {referral.invited_by.invite_code}"
            return self._build_response({"message": error_message}, status.HTTP_400_BAD_REQUEST)

        try:
            referer = User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            error_message = "Пользователь с указанным инвайт-кодом не найден"
            return self._build_response({"error": error_message}, status.HTTP_404_NOT_FOUND)

        referral.invited_by = referer
        referral.save()
        success_message = f"Вы стали рефералом пользователя с инвайт-кодом {referer.invite_code}"
        return self._build_response({"message": success_message})

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET-запрос, возвращая информацию о реферале.
        :param request: Запрос от клиента
        :return: Response с информацией о реферале
        """
        referral = request.user.invited_by
        if referral:
            referrer_info = f"Ваш реферер: {referral.invite_code}"
            return self._build_response({"message": referrer_info})
        return self._build_response({"message": "У вас нет реферера"})

    def _build_response(self, data, status_code=status.HTTP_200_OK):
        """
        Вспомогательный метод для построения ответа с поддержкой как HTML, так и JSON форматов.
        :param data: Данные для ответа
        :param status_code: HTTP статус код
        :return: Response объект
        """
        if self.request.accepted_renderer.format == 'html':
            return Response(data, status=status_code, template_name=self.template_name)
        return Response(data, status=status_code)


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
