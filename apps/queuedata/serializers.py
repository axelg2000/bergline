from rest_framework import serializers

from apps.queuedata.models import GuestlistSnapshot, MainQueueSnapshot


class MainQueueSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainQueueSnapshot
        fields = ["id", "location", "confidence_score", "recorded_at"]


class GuestlistSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestlistSnapshot
        fields = ["id", "location", "confidence_score", "recorded_at"]
