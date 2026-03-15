from django.contrib import admin

from apps.messages.models import ParsedMessage, RawMessage

admin.site.register(RawMessage)
admin.site.register(ParsedMessage)
