from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/algorithm/(?P<algorithm_id>\w+)/?$', consumers.AlgorithmWebSocketConsumer.as_asgi()),
    re_path(r'ws/algorithms/(?P<algorithm_name>\w+)/?$', consumers.AlgorithmWebSocketConsumer.as_asgi()),
    re_path(r'ws/algorithms/(?P<algorithm_name>\w+)/(?P<execution_id>\d+)/?$', consumers.AlgorithmWebSocketConsumer.as_asgi()),
    re_path(r'ws/algorithms/?$', consumers.AlgorithmWebSocketConsumer.as_asgi()),
]
