from slot_racer.client import Client
import asyncio
import threading

x, y = Client(), Client()
x.join_game()
y.join_game()

