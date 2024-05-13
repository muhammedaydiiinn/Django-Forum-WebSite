from django.urls import path

from . import views

urlpatterns = [
    path("", views.post_detail),
    path("<str:author>/<slug:slug>/", views.post_detail, name='post_detail'),
]
