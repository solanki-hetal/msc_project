from django.urls import path
from tracker import views

app_name = "tracker"

urlpatterns = [
    path("", views.home, name="home"),
]
