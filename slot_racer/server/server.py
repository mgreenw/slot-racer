# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to create a Server and its associated behaviours

# package imports
import time
import asyncio
import websockets
from ..game import Car, Track, Event
from ..communication import Serializer
from datetime import datetime, timedelta
from threading import Lock


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

    TODO: Consider creating a Monitor for max_id and client_skts
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
        self.server = websockets.serve(self.listener, self.host, self.port)
        print(f'Listening at {self.host}:{self.port}...')
        asyncio.ensure_future(self.loop())
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()

    async def loop(self):
        prev = None
        while True:
            if self.state.start_time is not None:
                now = datetime.now()
                if now > self.state.start_time:
                    dt = (now - prev).total_seconds()
                    self.gametime = (now - self.state.start_time).total_seconds()
                    self.track.update_all(self.gametime)
                    winner = self.track.check_winner()
                    if winner is not None and self.winner is None:
                        self.winner = winner
                        await self.update_all('winner', winner.id)

                    events = []
                    with self.events_lock:
                        events = self.events
                        self.events = []

                    await self.update_all('update', (self.gametime, events))
                else:
                    prev = self.state.start_time
            await asyncio.sleep(0.05)

    async def send(self, client, subject, data=None):
        message = self.serializer.compose(subject, data)
        await client.send(message)

    async def update_all(self, subject, data=None):
        message = self.serializer.compose(subject, data)
        await asyncio.wait([skt.send(message) for skt in self.state.clients])

    async def listener(self, skt, path):
        try:
            # There is a new socket! Find it's latency
            latency = await self.ping(skt)
            print(f'New Client Connected! Latency: {latency}')

            # Add the client to the server state and tell everyone about it
            me = self.state.add_client(skt, latency)
            client = self.state.clients[skt]

            # Update all with new car list. In each case, give
            # the client their own id
            all_cars = self.state.get_ids()
            for client_socket in self.state.clients:
                c = self.state.clients[client_socket]
                await self.send(client_socket, 'cars', (c.id, all_cars))

            # start listening for messages
            async for message in skt:
                await self.read_message(client, message)

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
        else:
            car = self.track.get_car_by_id(client.id)
            timestamp, speed, distance = parsed.data
            event = Event(parsed.subject, timestamp, speed, distance)
            car.append_events([event], self.gametime)
            with self.events_lock:
                self.events.append((client.id, parsed))

    async def send_countdown(self, client):
        t = 5 - client.latency
        await self.send(client.socket, 'begin_countdown', t)

    async def begin_countdown(self):
        if self.state.mode is not 'LOBBY':
            return
        self.state.mode = 'PLAY'
        for client in self.state.clients.values():
            self.track.add_participant(Car(client.id))
        self.state.start_time = datetime.now() + timedelta(seconds=5)
        await asyncio.wait([self.send_countdown(client) for client in self.state.clients.values()])

    async def ping(self, skt):
        repeat, latencies = 50, []
        for _ in range(repeat):
            start = time.time()
            await self.send(skt, 'ping')
            await skt.recv()
            end = time.time()
            latencies.append(end - start)
        return max(latencies)


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
        self.max_id += 1
        return client.id

    def remove_client(self, client_socket):
        self.track.remove_participant(self.clients[client_socket].id)
        del self.clients[client_socket]

    def get_ids(self):
        return [client.id for client in self.clients.values()]


