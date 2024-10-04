# faceRecognition/urls.py
from django.urls import path
from .views import facial_login, register,login_select

urlpatterns = [
    path("login/", facial_login, name="facial_login"),
    path("register/", register, name="register"),
    path("login__select/", login_select, name="login_select")
]
