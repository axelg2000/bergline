from django.db import models

from apps.users.models import User

SOURCE_CHOICES = [
    ("telegram", "Telegram"),
    ("reddit", "Reddit"),
    ("form", "Form"),
]


class RawMessage(models.Model):
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    external_id = models.CharField(max_length=255)
    content = models.TextField()
    posted_at = models.DateTimeField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("source", "external_id")

    def __str__(self):
        return f"[{self.source}] {self.external_id}"


class ParsedMessage(models.Model):
    raw_message = models.OneToOneField(RawMessage, on_delete=models.CASCADE, related_name="parsed")
    is_relevant = models.BooleanField()
    ai_model = models.CharField(max_length=50)
    parsed_at = models.DateTimeField(auto_now_add=True)

    queue_location = models.CharField(max_length=50, blank=True, default="")
    queue_location_confidence = models.FloatField(null=True, blank=True)
    queue_type = models.CharField(max_length=20, blank=True, default="")
    queue_speed = models.CharField(max_length=20, blank=True, default="")
    queue_speed_confidence = models.FloatField(null=True, blank=True)
    bouncer_name = models.CharField(max_length=255, blank=True, default="")
    bouncer_name_confidence = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Parsed: {self.raw_message.external_id} (relevant={self.is_relevant})"
