from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path("<int:consumer_id>/", views.consumer_details, name="consumer_details"),
        path('api/update-location/<int:consumer_id>/', views.update_location, name='update_location'),
        ]