# Author: Max Greenwald, Pulkit Jain
# 11/29/2018
#
# Module to communicate with the server

# package imports
import asyncio
import threading
import json
from ..game import state
from .renderer import Renderer
from .socket import start, Socket
from .protocol import get_protocol
from ..communication import Serializer


class Client(object):
    """Client defines how each client can interact with the server

    It is defined by the following attributes:
    - renderer: the Renderer that the client will use to display the game
                this also contains the track itself
    - id: the ID it has on the track in the server
    - websocket: the connection to the server

    A brief guide to our protocol [for more information, go to protocol.py]:
    - ping: returns the latency
    - cars: gets a list of all the car_ids
    - upda: update - basic message passing for debugging purposes

    It is defined by the following behaviours:
    - _run_socket(host, port): Internal function that is spawned on a new thread
          to create a persistent websocket connection to the server
    - receive_message(message): Consumes messages from the server
    - outgoing_message(): Waits for messages to be ready, and sends it asap to
          the server
    - join_game(host, port): Spawns a connection to the server and starts the
          game
    """
    def __init__(self):
        self.id            = None
        self.socket        = None
        self.socket_thread = None
        self.renderer      = Renderer(state.Track())
        self.protocol      = get_protocol()
        self.serializer    = Serializer()

        self.renderer.track.add_participant(state.Car(1))
        self.renderer.track.add_participant(state.Car(2))

    def _run_socket(self, host, port):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(
            start(self.socket))

    def _check_inbox(self):
        while True:
            message = self.serializer.read(self.socket.inbox.get())
            print('Client received message!')
            print(message)
            self.socket.outbox.put(self.serializer.compose('cars_response', message.subject))

    def join_game(self, host='localhost', port=8765):
        self.socket = Socket(host, port)
        self.socket_thread = \
            threading.Thread(target=self._run_socket, args=[host, port])
        self.socket_thread.start()
        inbox_thread = threading.Thread(target=self._check_inbox)
        inbox_thread.start()
        self.renderer.start()
