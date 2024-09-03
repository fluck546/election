from django.contrib import admin
from django.urls import path, include
from election_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('faceRecognition.urls')),
    path('vote/<int:round_id>/', views.vote_view, name='vote'),
    path('results/<int:round_id>/', views.results_view, name='results'),
]
