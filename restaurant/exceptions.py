from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {"error": "Something went wrong on our end."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Add custom error message format
    return Response(
        {"errors": response.data, "status_code": response.status_code},
        status=response.status_code,
    )
