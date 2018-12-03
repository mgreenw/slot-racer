# Author: Max Greenwald, Pulkit Jain
# 11/29/2018
#
# Module to communicate with the server

# package imports
import asyncio
import threading
from ..game import state
from .renderer import Renderer
from .socket import start, Socket
from ..communication import Serializer


class Client(object):
    """Client defines how each client can interact with the server

    It is defined by the following attributes:
    - id: the ID it has on the track in the server
    - socket: the connection to the server
    - renderer: the Renderer that the client will use to display the game
                this also contains the track itself
    - serializer: converts our data to a format we can use to communicate
    - running: boolean representing the state
    - my_car: my car
    - car_ids: ids of all cars on the track

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
        self.id         = None
        self.socket     = None
        self.renderer   = Renderer(state.Track(), self)
        self.serializer = Serializer()
        self.running    = True
        self.my_car     = None
        self.car_ids    = None

    def _run_socket(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        asyncio.get_event_loop().run_until_complete(start(self.socket))

    def join_game(self, host='localhost', port=8765):
        self.socket   = Socket(host, port)
        socket_thread = threading.Thread(target=self._run_socket, args=[])
        inbox_thread  = threading.Thread(target=self._check_inbox)
        #      Once setup is complete, start game
        socket_thread.start()
        inbox_thread.start()
        self.renderer.start()
        #      After renderer is quit, end game
        self.running = self.socket.running = False
        inbox_thread.join()
        socket_thread.join()

    def send(self, subject, data=None):
        message = self.serializer.compose(subject, data)
        self.socket.outbox.put(message)

    def _check_inbox(self):
        while self.running:
            # Block until the client has a new message. Then, handle the message
            message = self.serializer.read(self.socket.inbox.get())
            self.handle_message(message)

    def handle_message(self, message):
        subjects = dict(
            ping=self.ping,
            cars=self.cars,
            begin_countdown=self.begin_countdown
        )
        handler = subjects.get(message.subject, None)
        if handler is None:
            print(f'Receeived unknown message subject: {message.subject}')
            print()
        else:
            handler(message.data)

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


