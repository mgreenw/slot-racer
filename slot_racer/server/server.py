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
    - start_game(): starts a socket connection that clients can connect to
    - update_all(update): updates all the clients
    - listener(websocket, path): listens for messages from clients

    TODO: Consider creating a Monitor for max_id and client_skts
    """
    def __init__(self, host='localhost', port=8765):
        self.host        = host
        self.port        = port
        self.socket      = None
        self.update_time = 0.01
        self.listen_time = 0.01
        self.protocol    = get_protocol()
        self.state       = ServerState()
        self.serializer  = Serializer()

    def start_game(self):
        self.socket = websockets.serve(self.listener, self.host, self.port)
        print(f'Listening at {self.host}:{self.port}...')
        asyncio.ensure_future(self.update_all())
        asyncio.get_event_loop().run_until_complete(self.socket)
        asyncio.get_event_loop().run_forever()

    async def update_all(self, subject='test', data=None):
        message = self.serializer.compose(subject, data)
        for skt in self.state.clients:
            print('sending...')
            await skt.send(message)
        await asyncio.sleep(self.update_time)

    async def listener(self, skt, path):
        """
        DEV NOTES:
        - This function will be used to enforce our protocol
        - As soon as a client joins the game, we start our pinging to establish
          the latency
        - We are only going to use 4 letter codes to define our protocol
        """
        try:
            print(self.state.clients)
            if skt not in self.state.clients:
                latency = await self.protocol['pong'](skt)
                print('latency', latency)
                self.state.add_client(skt, 0.1)
                await self.update_all('cars', self.state.get_ids())
            async for message in skt:
                parsed = self.serializer.read(message)
                print(f'Received message:\nSubject: {parsed.subject}\nData: {parsed.data}\n\n')
                await asyncio.sleep(self.listen_time)
        except websockets.exceptions.ConnectionClosed as e:
            print(f'Connection with Client '
                  f'#{self.state.clients[skt][0]} closed!')
        finally:
            self.state.remove_client(skt)
            await self.update_all(f'cars {str(self.state.get_ids())}')


class ServerState(object):
    """ServerState represents the state of our server

    It is defined by the following attributes:
    - max_id: the maximum ID associated with a car
          NOTE: This is not a count of the total number of cars in our game.
                Clients may disconnect midway and in this case we delete them.
    - client_skts: a dictionary mapping client_websockets to
          [client_ids, latencies]
    - track: the server's copy of the track which is updated/modified based on
          client updates
    """
    def __init__(self):
        self.max_id  = 0
        self.clients = {}
        self.track   = Track()

    def add_client(self, client_socket, client_latency):
        self.clients[client_socket] = [self.max_id, client_latency]
        self.track.add_participant(Car(self.max_id))
        self.max_id += 1

    def remove_client(self, client_socket):
        self.track.remove_participant(self.clients[client_socket][0])
        del self.clients[client_socket]

    def get_ids(self):
        return [i[0] for i in self.clients.values()]


