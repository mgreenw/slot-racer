from slot_racer import client
import asyncio

socket = asyncio.get_event_loop().run_until_complete(client.Socket().connect())

renderer = client.Renderer()
renderer.start()
