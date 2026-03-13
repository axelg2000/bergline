from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.messages.authentication import APIKeyAuthentication
from apps.messages.models import RawMessage, Source
from apps.messages.serializers import MessageSubmitSerializer, RawMessageSerializer
from apps.messages.services.ai_analysis import analyze_message
from apps.users.authentication import GoogleTokenAuthentication


class ParsedMessageListView(generics.ListAPIView):
    """List of parsed messages (admin use)."""

    serializer_class = RawMessageSerializer
    queryset = RawMessage.objects.select_related("source", "parsed").prefetch_related("parsed__tags").order_by("-fetched_at")


class MessageSubmitView(APIView):
    """User form submission endpoint. Accepts Google Auth or API key."""

    authentication_classes = [GoogleTokenAuthentication, APIKeyAuthentication]

    def post(self, request):
        serializer = MessageSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        source, _ = Source.objects.get_or_create(name="form")

        raw_message = RawMessage.objects.create(
            source=source,
            user=request.user if hasattr(request.user, "pk") and request.user.pk else None,
            external_id=f"form_{timezone.now().timestamp()}",
            content=serializer.validated_data["content"],
            posted_at=timezone.now(),
        )

        parsed = analyze_message(raw_message)

        return Response(
            {
                "message_id": raw_message.id,
                "is_relevant": parsed.is_relevant if parsed else None,
            },
            status=status.HTTP_201_CREATED,
        )
