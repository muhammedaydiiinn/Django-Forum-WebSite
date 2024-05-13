from django.urls import path, include
from Content import views as content_views

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("Login/", include("Login.urls")),
    path("<str:author>/<slug:slug>/", content_views.post_detail, name='post_detail'),
    path("<str:author>/<slug:slug>/edit-post", content_views.update_post, name='edit_post'),
    path("create-topic", content_views.create_topic_button, name='create_topic'),
    path("create", views.create_topic, name='create_post'),
    path('increase-likes/<str:author>/<slug:slug>/', views.increase_likes, name='increase_likes'),
    path('check-like-status/<str:author>/<str:slug>/', views.check_like_status, name='check_like_status'),
    path('get-profile-image/', views.profile_image_view, name='get_profile_image_url'),
    path("profile/", include("Profile.urls")),
    path("search", views.search_view, name='search_view'),
]
