from slot_racer import Server
import sys


host, port = 'localhost', 8765

if len(sys.argv) > 1:
    host = sys.argv[1]
if len(sys.argv) > 2:
    port = int(sys.argv[2])

x = Server(host, port)
x.start_server()


