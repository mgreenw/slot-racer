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
        self.renderer      = Renderer(state.Track(), self)
        self.protocol      = get_protocol()
        self.serializer    = Serializer()
        self.running       = True
        self.my_car        = None
        self.car_ids       = None

    def _run_socket(self, host, port):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(
            start(self.socket))

    def send(self, subject, data=None):
        message = self.serializer.compose(subject, data)
        self.socket.outbox.put(message)

    def _check_inbox(self):
        while self.running:
            # Block until the client has a new message. Then, handle the message
            message = self.serializer.read(self.socket.inbox.get())
            self.handle_message(message)

    def join_game(self, host='localhost', port=8765):
        self.socket = Socket(host, port)
        socket_thread = threading.Thread(target=self._run_socket, args=[host, port])
        socket_thread.start()
        inbox_thread = threading.Thread(target=self._check_inbox)
        inbox_thread.start()
        self.renderer.start()

        # At this point, the renderer has quit. We want to signal the other
        # threads to end at this point
        self.running = False
        self.socket.running = False
        inbox_thread.join()
        socket_thread.join()

    # Message responses
    def ping(self, data):
        self.socket.outbox.put(self.serializer.compose('pong', None))

    def cars(self, data):
        my_car, all_cars = data
        self.car_ids = all_cars
        self.my_car = my_car
        print(f'Got new car list!\nMy id: {self.my_car}\nList: {self.car_ids}')

    def begin_countdown(self, time):
        self.renderer.switch_to_countdown(time)
        for car_id in self.car_ids:
            self.renderer.track.add_participant(state.Car(car_id))
        self.renderer.local_car = self.renderer.track.get_car_by_id(self.my_car)
        print(f'Begin countdown! {time}')

    def handle_message(self, message):
        subjects = dict(
            ping=self.ping,
            cars=self.cars,
            begin_countdown=self.begin_countdown
        )

        handler = subjects.get(message.subject, None)
        if handler is None:
            print(f'Receeived unknown message subject: {message.subject}')
            print
        else:
            handler(message.data)
