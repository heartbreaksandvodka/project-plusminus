from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def api_success(data=None, message=None, status_code=status.HTTP_200_OK):
    resp = {'success': True}
    if message:
        resp['message'] = message
    if data is not None:
        resp['data'] = data
    return Response(resp, status=status_code)

def api_error(message, error_type=None, status_code=status.HTTP_400_BAD_REQUEST, extra=None):
    resp = {'success': False, 'message': message}
    if error_type:
        resp['error_type'] = error_type
    if extra:
        resp.update(extra)
    return Response(resp, status=status_code)

def log_error(msg, exc=None):
    if exc:
        logger.error(f"{msg}: {exc}")
    else:
        logger.error(msg)
