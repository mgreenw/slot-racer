# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to create a Server and its associated behaviours

# package imports
import time
import asyncio
import websockets
from datetime import datetime, timedelta
from threading import Lock
import statistics
from ..game import Car, Track, Event
from ..communication import Serializer
from .extra import ServerState


class Server(object):
    """Server defines how a server interacts with its clients

    It is defined by the following attributes:
    - host: string representing the host
    - port: integer representing the port number to connect to
    - server: the open websocket for the server
    - update_time: time update_all loop waits for listener
    - listen_time: time listener loop waits for update_all
    - state: the state of the server defined below in ServerState
    - serializer: converts messages for reading and sending

    It is defined by the following behaviours:
    - start_server(): starts a socket connection that clients can connect to
    - update_all(update): updates all the clients
    - listener(websocket, path): listens for messages from clients
    """

    def __init__(self, host='localhost', port=8765):
        self.host        = host
        self.port        = port
        self.server      = None
        self.update_time = 0.01
        self.listen_time = 0.01
        self.state       = ServerState()
        self.serializer  = Serializer()
        self.track       = Track()
        self.events      = []
        self.events_lock = Lock()
        self.gametime   = 0
        self.winner      = None

    def start_server(self):
        """Start the server! Use the provided host and port, and run forever"""
        self.server = websockets.serve(self.listener, self.host, self.port)
        print(f'Listening at {self.host}:{self.port}...')
        asyncio.ensure_future(self.loop())
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    async def loop(self):
        while True:
            # If the game has a set start time, run the loop!
            if self.state.start_time is not None:
                now = datetime.now()
                self.game_time = (now - self.state.start_time).total_seconds()

                # Ensure the game has started
                if now > self.state.start_time:
                    self.track.update_all(self.game_time)

                    # Check for winners. If there is a winner, broadcast it
                    winner = self.track.check_winner()
                    if winner is not None and self.winner is None:
                        self.winner = winner
                        await self.update_all('winner', winner.id)

                    # Send out all of the most recent events and clear the list
                    # Only modify the events with access to the mutex
                    with self.events_lock:
                        events = self.events
                        self.events = []
                    await self.update_all('update', (self.game_time, events))

            # Wait 0.05 seconds between each server tick
            await asyncio.sleep(0.05)

    async def send(self, skt, subject, data=None):
        """Send a message to the given client socket"""
        message = self.serializer.compose(subject, data)
        await skt.send(message)

    async def update_all(self, subject, data=None):
        """Update all of the clients with the given message"""
        message = self.serializer.compose(subject, data)
        await asyncio.wait([skt.send(message) for skt in self.state.clients])

    async def listener(self, skt, path):
        """Listen for a new socket connection. On connection, update the server
        state and listen for messages from that client
        """
        try:
            # There is a new socket! Find its latency
            latency = await self.ping(skt)
            print(f'New Client Connected! Latency: {latency}')

            # Add the client to the server state and tell everyone about it
            self.state.add_client(skt, latency)
            client = self.state.clients[skt]

            # Update all with new car list. In each case, give
            # the client their own id. This is a special update all because
            # we include each client's own id in the message
            all_cars = self.state.get_ids()
            for client_socket in self.state.clients:
                other_client = self.state.clients[client_socket]
                await self.send(
                    client_socket,
                    'cars',
                    (other_client.id, all_cars)
                )

            # Start listening for messages
            async for message in skt:
                await self.read_message(client, message)

        except websockets.exceptions.ConnectionClosed as e:
            print(f'Connection with Client '
                  f'#{self.state.clients[skt][0]} closed!')

        finally:
            self.state.remove_client(skt)
            await self.update_all(f'cars {str(self.state.get_ids())}')

    async def read_message(self, client, message):
        """Read an incoming message"""
        parsed = self.serializer.read(message)

        # Handle the incoming message, splitting on the subject
        if parsed.subject == 'start_game':
            await self.begin_countdown()

        # The message is a game event. Append the event to the event list
        else:
            car = self.track.get_car_by_id(client.id)
            timestamp, speed, distance = parsed.data
            event = Event(parsed.subject, timestamp, speed, distance)
            car.append_events([event], self.gametime)
            with self.events_lock:
                self.events.append((client.id, parsed))

    async def send_countdown(self, client):
        """Send a game countdown to the given client. The message includes
        the number of seconds to start the game in
        """
        seconds = 5 - client.latency
        await self.send(client.socket, 'begin_countdown', seconds)

    async def begin_countdown(self):
        """Begin the countdown! Ensure the game is in the lobby"""
        if self.state.mode is not 'LOBBY':
            return

        # Put the game into play mode
        self.state.mode = 'PLAY'

        # Lock the participants and add them to the track
        for client in self.state.clients.values():
            self.track.add_participant(Car(client.id))

        # Send the countdown to every client
        self.state.start_time = datetime.now() + timedelta(seconds=5)
        clients =  self.state.clients.values()
        await asyncio.wait([self.send_countdown(client) for client in clients])

    async def ping(self, skt):
        """Ping the client 50 times and calculate the latency"""
        repeat, latencies = 50, []
        for _ in range(repeat):
            start = time.time()
            await self.send(skt, 'ping')
            await skt.recv()
            end = time.time()
            latencies.append(end - start)
        return statistics.mean(latencies) / 2
