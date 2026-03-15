from rest_framework import serializers

from apps.messages.models import ParsedMessage, RawMessage


class ParsedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedMessage
        fields = [
            "id", "is_relevant", "ai_model", "parsed_at",
            "queue_location", "queue_location_confidence", "queue_type",
            "queue_speed", "queue_speed_confidence",
            "bouncer_name", "bouncer_name_confidence",
        ]


class RawMessageSerializer(serializers.ModelSerializer):
    parsed = ParsedMessageSerializer(read_only=True)

    class Meta:
        model = RawMessage
        fields = ["id", "source", "external_id", "content", "posted_at", "fetched_at", "parsed"]


class MessageSubmitSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)
