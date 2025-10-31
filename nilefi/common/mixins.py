
from rest_framework.response import Response


class ResponseMixin:
    """Mixin for standardizing API responses."""

    def get_response(self, data=None, status=200, message=""):
        """Constructs a standardized API response."""
        return Response({"data": data, "message": message}, status=status)
