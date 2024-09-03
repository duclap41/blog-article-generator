from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserAuthor.index, name='index'),
    path('login', views.UserAuthor.login, name='login'),
    path('signup', views.UserAuthor.signup, name='signup'),
    path('logout', views.UserAuthor.logout, name='logout'),
]