from django.urls import path

from apps.messages.views import MessageSubmitView, ParsedMessageListView

app_name = "messages"

urlpatterns = [
    path("", ParsedMessageListView.as_view(), name="list"),
    path("submit/", MessageSubmitView.as_view(), name="submit"),
]
