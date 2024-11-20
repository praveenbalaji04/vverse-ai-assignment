from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        user_auth_token = request.META.get("HTTP_AUTH_TOKEN")
        if user_auth_token == "1534537f-f170-438f-b56a-58644a84233f":  # TEMPORARY_STATIC_AUTH_TOKEN
            return None

        raise AuthenticationFailed
