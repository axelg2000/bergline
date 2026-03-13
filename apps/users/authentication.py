"""Google ID token authentication for form-submitting users."""

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import authentication, exceptions

from apps.users.models import User


class GoogleTokenAuthentication(authentication.BaseAuthentication):
    """Authenticate users via Google ID token in the Authorization header.

    Expects: Authorization: Bearer <google_id_token>
    Verifies the token with Google, creates the user if needed, and
    returns the user object.
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ", 1)[1]

        try:
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request()
            )
        except ValueError:
            raise exceptions.AuthenticationFailed("Invalid Google token.")

        google_id = idinfo["sub"]
        email = idinfo.get("email", "")

        user, _ = User.objects.get_or_create(
            google_id=google_id,
            defaults={"email": email},
        )

        return (user, None)
