# election_project/urls.py
from django.contrib import admin
from django.urls import path, include
from election_app import views


urlpatterns = [
    path("/", include("faceRecognition.urls")),
    path("admin/", admin.site.urls),
    path("admin-panel/", views.admin_view, name="admin"),
    path("vote/<int:round_id>/", views.vote_view, name="vote"),
    path("results/<int:round_id>/", views.results_view, name="results"),
]
