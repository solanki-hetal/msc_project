from django.urls import path
from tracker import views

app_name = "tracker"

urlpatterns = [
    path("", views.home, name="home"),
    path("tokens/", views.TokenListView.as_view(), name="token_list"),
    path("tokens/create/", views.TokenCreateView.as_view(), name="token_create"),
    path("tokens/<int:pk>/edit/", views.TokenEditView.as_view(), name="token_edit"),
]
