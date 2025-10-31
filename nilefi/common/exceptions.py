
from rest_framework.exceptions import APIException


class NileFiException(APIException):
    """Base exception class for NileFi."""

    default_detail = "An unexpected error occurred."
    default_code = "error"
