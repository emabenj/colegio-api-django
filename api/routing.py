from django.urls import re_path
from .consumers import ChatConsumer,OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<user1_id>\d+)-(?P<user2_id>\d+)/$', ChatConsumer.as_asgi()),
                         
    re_path(r'ws/chat/online/(?P<aula_id>\w+)/$', OnlineStatusConsumer.as_asgi()),
]
