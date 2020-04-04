from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from apps.trips.middleware import TokenAuthMiddlewareStack
from taxi.apps.trips.consumers import TaxiConsumer

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('taxi/', TaxiConsumer),
        ])
    ),
})
