# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to create a Server and its associated behaviours

# package imports
import re
import asyncio
import websockets
from .protocol import get_protocol
from ..game import Car, Track
from collections import namedtuple
import json
from ..communication import Serializer
from datetime import datetime, timedelta
from threading import Lock

class Server(object):
    """Server defines how a server interacts with its clients

    It is defined by the following attributes:
    - host: string representing the host
    - port: integer representing the port number to connect to
    - socket: the open websocket for the server
    - update_time: time update_all loop waits for listener
    - listen_time: time listener loop waits for update_all
    - protocol: a dictionary containing our messaging protocol as a mapping of
          messages to functions
    - state: the state of the server defined below in ServerState

    A brief guide to our protocol [for more information, go to protocol.py]:
    - ping: returns the latency
    - cars: sends out a list of all the cars

    It is defined by the following behaviours:
    - start_server(): starts a socket connection that clients can connect to
    - update_all(update): updates all the clients
    - listener(websocket, path): listens for messages from clients

    TODO: Consider creating a Monitor for max_id and client_skts
    """
    def __init__(self, host='localhost', port=8765):
        self.host        = host
        self.port        = port
        self.server      = None
        self.update_time = 0.01
        self.listen_time = 0.01
        self.protocol    = get_protocol()
        self.state       = ServerState()
        self.serializer  = Serializer()
        self.track       = Track()
        self.events      = []
        self.events_lock = Lock()

    def start_server(self):
        self.server = websockets.serve(self.listener, self.host, self.port)
        print(f'Listening at {self.host}:{self.port}...')
        asyncio.ensure_future(self.loop())
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    async def loop(self):
        while True:
            if self.state.start_time is not None:
                now = datetime.now()
                if now > self.state.start_time:
                    game_time = (now - self.state.start_time).total_seconds()
                    events = []
                    with self.events_lock:
                        events = self.events
                        self.events = []

                    await self.update_all('update', (game_time, events))
            await asyncio.sleep(0.05)

    async def send(self, client, subject, data=None):
        message = self.serializer.compose(subject, data)
        await client.send(message)

    async def update_all(self, subject, data=None):
        message = self.serializer.compose(subject, data)
        await asyncio.wait([skt.send(message) for skt in self.state.clients])

    async def listener(self, skt, path):
        """
        DEV NOTES:
        - This function will be used to enforce our protocol
        - As soon as a client joins the game, we start our pinging to establish
          the latency
        - We are only going to use 4 letter codes to define our protocol
        """
        try:
            # There is a new socket! Find it's latency
            latency = await self.protocol['pong'](skt)
            print(f'New Client Connected! Latency: {latency}')

            # Add the client to the server state
            self.state.add_client(skt, latency)
            client = self.state.clients[skt]
            await self.update_all('cars', (client.id, self.state.get_ids()))
            async for message in skt:
                await self.read_message(client, message)
                await asyncio.sleep(self.listen_time)
        except websockets.exceptions.ConnectionClosed as e:
            print(f'Connection with Client '
                  f'#{self.state.clients[skt][0]} closed!')
        finally:
            self.state.remove_client(skt)
            await self.update_all(f'cars {str(self.state.get_ids())}')

    async def read_message(self, client, message):
        parsed = self.serializer.read(message)
        if parsed.subject == 'start_game':
            await self.begin_countdown()
            for car in self.state.clients.values():
                self.track.add_participant(Car(car.id))
        else:
            with self.events_lock:
                self.events.append((client.id, parsed))
        print(f'Received message:\nClient: {client.id}\nSubject: {parsed.subject}\nData: {parsed.data}\n')

    async def send_countdown(self, client):
        time = 5 - client.latency
        await self.send(client.socket, 'begin_countdown', time)

    async def begin_countdown(self):
        if self.state.mode is not 'LOBBY':
            return
        self.state.start_time = datetime.now() + timedelta(seconds=5)
        await asyncio.wait([self.send_countdown(client) for client in self.state.clients.values()])


class Client(object):
    def __init__(self, id, socket, latency):
        self.id = id
        self.socket = socket
        self.latency = latency

class ServerState(object):
    """ServerState represents the state of our server

    It is defined by the following attributes:
    - max_id: the maximum ID associated with a car
          NOTE: This is not a count of the total number of cars in our game.
                Clients may disconnect midway and in this case we delete them.
    - clients: a dictionary mapping client_websockets to
          [client_ids, latencies]
    - track: the server's copy of the track which is updated/modified based on
          client updates
    """
    def __init__(self):
        self.mode   = 'LOBBY'
        self.clients = {}
        self.track   = Track()
        self.max_id  = 0
        self.start_time = None

    def get_update(self):
        pass

    def add_client(self, client_socket, client_latency):
        client = Client(self.max_id, client_socket, client_latency)
        self.clients[client.socket] = client
        self.track.add_participant(Car(client.id))
        self.max_id += 1
        return client.id

    def remove_client(self, client_socket):
        self.track.remove_participant(self.clients[client_socket].id)
        del self.clients[client_socket]

    def get_ids(self):
        return [client.id for client in self.clients.values()]


