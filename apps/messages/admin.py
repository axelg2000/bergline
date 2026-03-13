from django.contrib import admin

from apps.messages.models import MessageTag, ParsedMessage, RawMessage, Source

admin.site.register(Source)
admin.site.register(RawMessage)
admin.site.register(ParsedMessage)
admin.site.register(MessageTag)
