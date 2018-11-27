import asyncio
import websockets

async def listener(websocket, path):
    name = await websocket.recv()
    print(f"< {name}")

    greeting = f"Hello {name}!"

    await websocket.send(greeting)
    print(f"> {greeting}")

def start():
    server = websockets.serve(listener, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

# Some rules:
#  If a client's connection is dropped, they are immediately withdrawn from the race
#
