from . import views
from django.urls import path, include

urlpatterns = [
  path('status/', views.projects_status, name='projects_status'),
  path('download_projects_progress/', views.download_projects_progress, name='download_projects_progress')
  ]