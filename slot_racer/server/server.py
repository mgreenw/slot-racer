import asyncio
import websockets

sockets = set()

async def tick():
    counter = 0
    while True:
        print('tick')
        counter += 1
        for socket in sockets:
            await socket.send('hey!' + str(counter))
        await asyncio.sleep(1)

async def listener(websocket, path):
    sockets.add(websocket)
    async for message in websocket:
        print(f"Received message: {message}")

def start():
    server = websockets.serve(listener, 'localhost', 8765)
    print("listening on port 8765")
    asyncio.ensure_future(tick())
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

# Some rules:
#  If a client's connection is dropped, they are immediately withdrawn from the race
#
