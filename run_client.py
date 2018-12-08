from slot_racer.client import Client
import sys


host, port = 'localhost', 8765

if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])

x = Client()
x.join_game(host, port)

