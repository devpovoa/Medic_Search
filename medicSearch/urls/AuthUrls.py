from django.urls import path, include
from medicSearch.views.AuthView import login_view, register_view, logout_view, recover_view, change_password_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", logout_view, name="logout"),
    path("recovery/", recover_view, name="recovery"),
    path("change-password/<str:token>", change_password_view, name="change_password"),
    path('auth/', include('social_django.urls', namespace='social')),
]
