from django.urls import path
from . import views

urlpatterns = [
  path('', views.index),
  path('inquiries', views.inquiries, name="inquiries"),
  path('responses', views.responses, name="responses"),
  path('applications', views.applications, name="applications"),
  path('login', views.loginPage, name="login"),
  path('register', views.registerPage, name="register"),
  path('logout', views.logoutUser, name="logout"),
]
