# Author: Max Greenwald, Pulkit Jain
# 12/1/2018
#
# Module to create a Server and its associated behaviours

# package imports
import asyncio
import websockets
from .protocol import get_protocol
from ..game import Car, Track


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

    It is defined by the following behaviours:
    - start_game(): starts a socket connection that clients can connect to
    - update_all(): updates all the clients
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

    def start_game(self):
        self.socket = websockets.serve(self.listener, self.host, self.port)
        print(f'Listening at {self.host}:{self.port}')
        asyncio.ensure_future(self.update_all())
        asyncio.get_event_loop().run_until_complete(self.socket)
        asyncio.get_event_loop().run_forever()

    async def update_all(self):
        while True:
            for skt in self.state.clients:
                await skt.send(f'UPDATE')
            await asyncio.sleep(self.update_time)

    async def listener(self, skt, path):
        """
        DEV NOTES:
        - This function will be used to enforce our protocol
        - As soon as a client joins the game, we start our pinging to establish
          the latency
        """
        try:
            latency = await self.protocol['ping'](skt)
            self.state.add_client(skt, latency)
            async for message in skt:
                if message in self.protocol:
                    self.protocol[message]()
                await asyncio.sleep(self.listen_time)
        except websockets.exceptions.ConnectionClosed as e:
            print(f'Connection with Client '
                  f'#{self.state.clients[skt][0]} closed!')
        finally:
            self.state.remove_client(skt)


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


