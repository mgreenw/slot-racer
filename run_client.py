from slot_racer.client import run_socket, Renderer
import asyncio
import threading

async def outgoing_message():
    await asyncio.sleep(1)
    return 'ping'

async def receive_message(message):
    print(message)

socket_thread = run_socket(receive_message=receive_message, outgoing_message=outgoing_message)

renderer = Renderer()
renderer.start()
