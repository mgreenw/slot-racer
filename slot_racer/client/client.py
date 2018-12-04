# Author: Max Greenwald, Pulkit Jain
# 11/29/2018
#
# Module to communicate with the server

# package imports
import asyncio
import threading
from ..game import state, Event
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
    - my_car: car id of client's car -- used during starting the game
    - car_ids: ids of all cars on the track -- used during starting the game

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
            message = self.serializer.read(self.socket.inbox.get())
            self.handle_message(message)

    def handle_message(self, message):
        subjects = dict(
            ping=self.ping,
            cars=self.cars,
            begin_countdown=self.begin_countdown,
            update=self.server_update
        )
        handler = subjects.get(message.subject, None)
        if handler is None:
            print(f'Received unknown message subject: {message.subject}')
            print()
        else:
            handler(message.data)

    # Messaging Protocol ------------------------------------------------------
    def ping(self, data):
        self.socket.outbox.put(self.serializer.compose('pong', None))

    def cars(self, data):
        self.my_car, self.car_ids = data
        self.id = self.my_car
        print(f'Got new car list!\nMy id: {self.my_car}\nList: {self.car_ids}')

    def begin_countdown(self, time):
        self.renderer.switch_to_countdown(time)
        for car_id in self.car_ids:
            self.renderer.track.add_participant(state.Car(car_id))

            print(f"ADDING {car_id}. Self: {self.id}")
        self.renderer.local_car = self.renderer.track.get_car_by_id(self.id)
        print(f'Begin countdown! {time}')

    def server_update(self, data):
        server_time, events = data
        if len(events) > 0:
            events = [(car_id, event) for car_id, event in events if car_id != self.id]

            # Todo: generalize this for many cars
            if len(events) > 0:
                car_id, event = events[0]
                car = self.renderer.track.get_car_by_id(car_id)
                events_to_insert = []
                for car_id, event in events:
                    event_type, data = event
                    timestamp, speed, distance = data
                    e = Event(event_type, timestamp, speed, distance)
                    events_to_insert.append(e)

                car.append_events(events_to_insert, self.renderer.game_time)


