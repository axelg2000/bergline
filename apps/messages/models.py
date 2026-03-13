from django.db import models

from apps.users.models import User


class Source(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class RawMessage(models.Model):
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="raw_messages")
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

    def __str__(self):
        return f"Parsed: {self.raw_message.external_id} (relevant={self.is_relevant})"


class MessageTag(models.Model):
    TAG_TYPES = [
        ("queue_location", "Queue Location"),
        ("queue_speed", "Queue Speed"),
        ("bouncer_name", "Bouncer Name"),
    ]
    parsed_message = models.ForeignKey(ParsedMessage, on_delete=models.CASCADE, related_name="tags")
    tag_type = models.CharField(max_length=50, choices=TAG_TYPES)
    extracted_value = models.CharField(max_length=255)
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tag_type}: {self.extracted_value} ({self.confidence_score})"
