from django.contrib import admin

from apps.queuedata.models import GuestlistSnapshot, MainQueueSnapshot

admin.site.register(MainQueueSnapshot)
admin.site.register(GuestlistSnapshot)
