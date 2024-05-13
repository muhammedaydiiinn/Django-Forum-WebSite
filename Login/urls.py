from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_views, name="login"),
    path("register/", views.sign_views, name="register"),
    path('logout/', views.logout_user, name='logout'),
]
