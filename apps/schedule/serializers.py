from rest_framework import serializers

from apps.schedule.models import DJSchedule


class DJScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DJSchedule
        fields = ["id", "stage", "dj_name", "start_time", "end_time"]
