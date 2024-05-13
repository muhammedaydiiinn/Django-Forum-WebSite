from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_profile, name='profile'),
    path('update-profile-picture', views.update_profile_picture, name='update_profile_picture'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('my_topics', views.my_topics, name='my_topics')
]
