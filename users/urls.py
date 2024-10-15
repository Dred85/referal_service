from django.urls import path

from users import views
from users.apps import UsersConfig
from users.views import (MyTokenObtainPairView, MyTokenRefreshView,
                         SetReferrerAPIView, UserRetrieveAPIView)

app_name = UsersConfig.name

urlpatterns = [
    path("auth/get_code/", views.UserGetCodeAPIView.as_view(), name="get_code"),
    path("auth/send_code/", MyTokenObtainPairView.as_view(), name="send_code"),
    path("auth/refresh/", MyTokenRefreshView.as_view(), name="token_refresh"),
    path("set_referrer/", SetReferrerAPIView.as_view(), name="set_referrer"),
    path("retrieve/", UserRetrieveAPIView.as_view(), name="retrieve"),
]
