from rest_framework import serializers

from apps.messages.models import MessageTag, ParsedMessage, RawMessage, Source


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ["id", "name"]


class MessageTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageTag
        fields = ["id", "tag_type", "extracted_value", "confidence_score", "created_at"]


class ParsedMessageSerializer(serializers.ModelSerializer):
    tags = MessageTagSerializer(many=True, read_only=True)

    class Meta:
        model = ParsedMessage
        fields = ["id", "is_relevant", "ai_model", "parsed_at", "tags"]


class RawMessageSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    parsed = ParsedMessageSerializer(read_only=True)

    class Meta:
        model = RawMessage
        fields = ["id", "source", "external_id", "content", "posted_at", "fetched_at", "parsed"]


class MessageSubmitSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=5000)
