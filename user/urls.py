from django.urls import path
from user import views


app_name = "user"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_user, name="logout"),
]
