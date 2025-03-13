from django.urls import re_path
from . import consumers

from django.urls import path
from .consumers import AttendanceConsumer

websocket_urlpatterns = [
    path("ws/myapp/", consumers.AttendanceConsumer.as_asgi()),
]
