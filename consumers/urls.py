from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path("<int:consumer_id>/", views.consumer_details, name="consumer_details"),
        path("test_api/", views.test_api)
        ]