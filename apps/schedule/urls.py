from django.urls import path

from apps.schedule.views import DJScheduleListView, DJScheduleNowView

app_name = "schedule"

urlpatterns = [
    path("now/", DJScheduleNowView.as_view(), name="now"),
    path("", DJScheduleListView.as_view(), name="list"),
]
