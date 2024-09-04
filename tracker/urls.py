from django.urls import path

from tracker import views

app_name = "tracker"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("tokens/", views.TokenListView.as_view(), name="gittoken_list"),
    path("tokens/create/", views.TokenCreateView.as_view(), name="gittoken_create"),
    path("tokens/<int:pk>/edit/", views.TokenEditView.as_view(), name="gittoken_edit"),
    path("tokens/<int:pk>/delete/", views.delete_token, name="gittoken_delete"),
    path("repository/", views.RepositoryListView.as_view(), name="repository_list"),
    path(
        "repository/<int:pk>/analysis/",
        views.RepositoryStatsView.as_view(),
        name="repository_analysis",
    ),
    path(
        "repository/<int:repository_id>/commits/",
        views.CommitListView.as_view(),
        name="commit_list",
    ),
    path(
        "repository/<int:repository_id>/commits/<int:commit_id>/",
        views.CommitDetailView.as_view(),
        name="commit_detail",
    ),
    path(
        "anomalies/",
        view=views.AnomalyListView.as_view(),
        name="anomaly_list",
    ),
    path(
        "webhook/",
        view=views.webhook_listener_view,
        name="webhook_listener",
    ),
]
