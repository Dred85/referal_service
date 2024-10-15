from django.contrib.auth import get_user_model
from rest_framework import generics, status, views
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.renderers import TemplateHTMLRenderer
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

    def get_or_create(self, request, *args, **kwargs):
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
        raise NotImplementedError

    def get_success_headers(self, data):
        try:
            return {"Location": str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def post(self, request, *args, **kwargs):
        return self.get_or_create(request, *args, **kwargs)


class UserGetEnterCodeMixin(GetOrCreateModelMixin):
    model = User
    serializer_class = UserPhoneSerializer

    def perform_get_or_create(self, serializer):
        user, created = self.model.objects.get_or_create(
            **serializer.validated_data, defaults={"invite_code": create_invite_code()}
        )
        enter_code = create_enter_code()
        self.request.session[user.phone] = enter_code
        send_enter_code(user.phone, enter_code)

        return created


class UserGetCodeAPIView(UserGetEnterCodeMixin, generics.GenericAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "get_code.html"

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class()
        return Response({"serializer": serializer})


class MyTokenObtainPairView(TokenObtainPairView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "send_code.html"
    permission_classes = (AllowAny,)
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
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
        serializer = self.serializer_class()
        return Response({"serializer": serializer})


class MyTokenRefreshView(TokenRefreshView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "refresh.html"
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
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
        serializer = self.get_serializer_class()()
        return Response({"serializer": serializer})


class SetReferrerAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "set_referrer.html"

    def post(self, request):
        invite_code = request.data.get("invite_code", "")
        referral = request.user
        if referral.invite_code == invite_code:
            return Response({"message": "You cannot enter your own invite code"})
        if referral.invited_by is not None:
            return Response(
                {
                    "message": f"You have already been referral "
                    f"of user with invite code {referral.invited_by.invite_code}"
                }
            )

        referer = get_object_or_404(User.objects.filter(invite_code=invite_code))

        referral.invited_by = referer
        referral.save()
        return Response(
            {
                "message": f"You have become referral of user with invite code {referer.invite_code}"
            }
        )

    def get(self, request, *args, **kwargs):
        return Response()


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserRetrieveSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "retrieve.html"

    def get_object(self):
        return self.request.user
