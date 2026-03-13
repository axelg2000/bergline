from rest_framework import generics

from apps.queuedata.models import GuestlistSnapshot, MainQueueSnapshot
from apps.queuedata.serializers import GuestlistSnapshotSerializer, MainQueueSnapshotSerializer


class MainQueueLatestView(generics.ListAPIView):
    """Most recent main queue snapshots (one per location)."""

    serializer_class = MainQueueSnapshotSerializer

    def get_queryset(self):
        return (
            MainQueueSnapshot.objects
            .order_by("location", "-recorded_at")
            .distinct("location")
        )


class MainQueueHistoryView(generics.ListAPIView):
    """Historical main queue data."""

    serializer_class = MainQueueSnapshotSerializer
    queryset = MainQueueSnapshot.objects.order_by("-recorded_at")


class GuestlistLatestView(generics.ListAPIView):
    """Most recent guestlist snapshots (one per location)."""

    serializer_class = GuestlistSnapshotSerializer

    def get_queryset(self):
        return (
            GuestlistSnapshot.objects
            .order_by("location", "-recorded_at")
            .distinct("location")
        )


class GuestlistHistoryView(generics.ListAPIView):
    """Historical guestlist data."""

    serializer_class = GuestlistSnapshotSerializer
    queryset = GuestlistSnapshot.objects.order_by("-recorded_at")
