import hmac

from django.conf import settings
from rest_framework import authentication, exceptions


class APIKeyUser:
    """Minimal user-like object for API key authentication."""

    is_authenticated = True


class APIKeyAuthentication(authentication.BaseAuthentication):
    """Authenticate requests using X-API-Key header."""

    def authenticate(self, request):
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return None
        if not hmac.compare_digest(api_key, settings.BERGLINE_API_KEY):
            raise exceptions.AuthenticationFailed("Invalid API key.")
        return (APIKeyUser(), None)
