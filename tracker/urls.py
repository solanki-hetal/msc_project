from django.urls import path
from tracker import views

app_name = "tracker"

urlpatterns = [
    path("", views.home, name="home"),
    path("tokens/", views.TokenListView.as_view(), name="gittoken_list"),
    path("tokens/create/", views.TokenCreateView.as_view(), name="gittoken_create"),
    path("tokens/<int:pk>/edit/", views.TokenEditView.as_view(), name="gittoken_edit"),
    path("repositories/", views.RepositoryListView.as_view(), name="repository_list"),
]
