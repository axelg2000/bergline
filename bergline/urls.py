from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/messages/", include("apps.messages.urls")),
    path("api/queue/", include("apps.queuedata.urls")),
    path("api/schedule/", include("apps.schedule.urls")),
]
