from django.urls import path

from apps.queuedata.views import (
    GuestlistHistoryView,
    GuestlistLatestView,
    MainQueueHistoryView,
    MainQueueLatestView,
)

app_name = "queuedata"

urlpatterns = [
    path("main/latest/", MainQueueLatestView.as_view(), name="main-latest"),
    path("main/history/", MainQueueHistoryView.as_view(), name="main-history"),
    path("guestlist/latest/", GuestlistLatestView.as_view(), name="guestlist-latest"),
    path("guestlist/history/", GuestlistHistoryView.as_view(), name="guestlist-history"),
]
