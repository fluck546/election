from django.contrib import admin
from django.urls import path, include
from election_app import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("faceRecognition.urls")),

    path("results/<int:round_id>/", views.results_view, name="results"),
    path("", views.index, name="index"),
    path("logout/", views.custom_logout, name="logout"),
    path("manage_users/", views.manage_users, name="manage_users"),
    path("get_user_data/<int:user_id>/", views.get_user_data, name="get_user_data"),
    path("edit_user/<int:user_id>/", views.edit_user, name="edit_user"),
    path("delete_user/<int:user_id>/", views.delete_user, name="delete_user"),
    path("manage_rounds/", views.manage_rounds, name="manage_rounds"),
    path("edit_round/<int:round_id>/", views.edit_round, name="edit_round"),
    path("delete_round/<int:round_id>/", views.delete_round, name="delete_round"),
    path("manage_candidates/", views.manage_candidates, name="manage_candidates"),
    path(
        "edit_candidate/<int:candidate_id>/",
        views.edit_candidate,
        name="edit_candidate",
    ),
    path(
        "delete_candidate/<int:candidate_id>/",
        views.delete_candidate,
        name="delete_candidate",
    ),
    path("add_user/", views.add_user, name="add_user"),
    path("get_round_data/<int:round_id>/", views.get_round_data, name="get_round_data"),
    path(
        "get_candidate_data/<int:candidate_id>/",
        views.get_candidate_data,
        name="get_candidate_data",
    ),
    path("get_election_rounds/", views.get_election_rounds, name="get_election_rounds"),
    path("manage_votes/", views.manage_votes, name="manage_votes"),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('download_pdf_results/<int:round_id>/', views.download_pdf_results, name='download_pdf_results'),
     path('generate_results/', views.results_selection_page, name='generate_results'),
     path('get_round_votes/<int:round_id>/', views.get_round_votes, name='get_round_votes'),
     

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
