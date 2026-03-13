from django.utils import timezone
from rest_framework import generics

from apps.schedule.models import DJSchedule
from apps.schedule.serializers import DJScheduleSerializer


class DJScheduleNowView(generics.ListAPIView):
    """Which DJ is playing right now, per stage."""

    serializer_class = DJScheduleSerializer

    def get_queryset(self):
        now = timezone.now()
        return DJSchedule.objects.filter(start_time__lte=now, end_time__gte=now)


class DJScheduleListView(generics.ListAPIView):
    """Full DJ schedule."""

    serializer_class = DJScheduleSerializer
    queryset = DJSchedule.objects.all()
