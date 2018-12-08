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
    - _run_socket(host, port): Internal function that is spawned on a new
          thread to create a persistent websocket connection to the server
    - _check_inbox(): Gets message from inbox and handles it
    - send(subject, data): Serializes and sends message to outbox
    - join_game(host, port): Spawns a connection to the server and starts the
          game, once we're done it ends the game
    - handle_message(message): Handles incoming message through defined message
          protocols
    -
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

    def _check_inbox(self):
        while self.running:
            message = self.serializer.read(self.socket.inbox.get())
            self.handle_message(message)

    def send(self, subject, data=None):
        message = self.serializer.compose(subject, data)
        self.socket.outbox.put(message)

    # Joins a game specified by host and port, and exits once client is done
    def join_game(self, host='localhost', port=8765):
        self.socket   = Socket(host, port)
        socket_thread = threading.Thread(target=self._run_socket, args=[])
        inbox_thread  = threading.Thread(target=self._check_inbox)

        # Once setup is complete, start game
        socket_thread.start()
        inbox_thread.start()
        self.renderer.start()

        # After renderer is quit, end game
        self.running = self.socket.running = False
        inbox_thread.join()
        socket_thread.join()

    # handler for all incoming messages
    def handle_message(self, message):
        subjects = dict(
            ping=self.ping,
            cars=self.cars,
            begin_countdown=self.begin_countdown,
            update=self.server_update,
            winner=self.winner
        )
        handler = subjects.get(message.subject, None)
        if handler is None:
            print(f'Received unknown message subject: {message.subject}\n')
        else:
            handler(message.data)

    # Messaging Protocol ------------------------------------------------------
    def ping(self, data):
        """Used for syncing times with the server"""
        self.socket.outbox.put(self.serializer.compose('pong', None))

    def cars(self, data):
        """Receives updates from server on number of cars in track"""
        self.my_car, self.car_ids = data
        self.id = self.my_car
        print(f'Got new car list!\nMy id: {self.my_car}\nList: {self.car_ids}')

    def begin_countdown(self, time):
        """Starts countdown before game"""
        self.renderer.switch_to_countdown(time)
        for car_id in self.car_ids:
            self.renderer.track.add_participant(state.Car(car_id))

            print(f"ADDING {car_id}. Self: {self.id}")
        self.renderer.local_car = self.renderer.track.get_car_by_id(self.id)
        print(f'Begin countdown! {time}')

    def server_update(self, data):
        """Receives update from server on state and events"""
        server_time, events = data
        if len(events) > 0:
            events = [(car_id, event) for car_id, event in events
                      if car_id != self.id]
            if len(events) > 0:
                car_id, event = events[0]
                car = self.renderer.track.get_car_by_id(car_id)
                events_to_insert = []
                for car_id, event in events:
                    event_type, data = event
                    timestamp, speed, distance = data
                    e = Event(event_type, timestamp, speed, distance)
                    events_to_insert.append(e)

                car.append_events(events_to_insert, self.renderer.gametime)

    def winner(self, data):
        """Declares the winner"""
        self.renderer.set_winner(data)


