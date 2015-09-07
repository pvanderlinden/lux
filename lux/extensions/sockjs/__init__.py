'''
Websocket handler for SockJS clients.
'''
import lux
from pulsar.apps.data import create_store
from pulsar.apps import rpc

from lux import Parameter

from .socketio import SocketIO
from .ws import LuxWs


__all__ = ['LuxWs', 'SocketIO']


class Extension(lux.Extension):

    _config = [
        Parameter('WS_URL', '/ws', 'Websocket base url'),
        Parameter('WS_HANDLER', LuxWs, 'Websocket handler'),
        Parameter('PUBSUB_STORE', None,
                  'Connection string for a Publish/Subscribe data-store'),
        Parameter('WEBSOCKET_HARTBEAT', 25, 'Hartbeat in seconds'),
        Parameter('WEBSOCKET_AVAILABLE', True,
                  'Server handle websocket'),
    ]

    def on_config(self, app):
        app.add_events(('on_websocket_open', 'on_websocket_close'))

    def middleware(self, app):
        '''Add middleware to edit content
        '''
        handler = app.config['WS_HANDLER']
        if handler:
            socketio = SocketIO(app.config['WS_URL'], handler(app))
            self.websocket = socketio.handle
            return [socketio]

    def on_loaded(self, app):
        '''Once the application has loaded, create the pub/sub
        handler used to publish messages to channels as
        well as subscribe to channels
        '''
        pubsub_store = app.config['PUBSUB_STORE']
        if pubsub_store:
            self.pubsub_store = create_store(pubsub_store)
            self.websocket.pubsub = self.pubsub_store.pubsub()
