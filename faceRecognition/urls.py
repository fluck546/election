# faceRecognition/urls.py
from django.urls import path
from .views import facial_login, register

urlpatterns = [
    path("login/", facial_login, name="facial_login"),
    path("register/", register, name="register"),
]
