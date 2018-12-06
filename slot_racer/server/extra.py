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