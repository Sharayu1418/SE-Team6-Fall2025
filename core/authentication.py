"""
Custom authentication classes for the API.
"""

from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Session authentication that doesn't enforce CSRF.
    
    Use this for SPA frontends that handle CSRF via headers.
    The frontend should still send the X-CSRFToken header,
    but this won't reject requests without it during development.
    """
    
    def enforce_csrf(self, request):
        """
        Skip CSRF check - the frontend handles this via the X-CSRFToken header.
        """
        return None  # Don't enforce CSRF

