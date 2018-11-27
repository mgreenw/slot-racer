import pyxel
import math
from enum import Enum

from ..game import state

# Define the width and height of the screen
# This makes for a nice 16x9 screen
WIDTH = 255
HEIGHT = 143

# Client-only states
# - Menu
# - Lobby
# - Playing

# Goals
# 1. make the state transitions work
# 2. import the state and begin to work with it
# 3. Look into the websocket stuff

import asyncio
import websockets

async def hello():
    async with websockets.connect(
            'ws://localhost:8765') as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

class Button(object):
    def __init__(self, text, x, y, w, h, background_color, text_color):
        self.text = text
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.background_color = background_color
        self.text_color = text_color

    def render(self):
        pyxel.rect(self.x, self.y, self.x + self.w, self.y + self.h, self.background_color)
        pyxel.text(self.x + 7, self.y + 5, self.text, self.text_color)
        if pyxel.btnr(2000) and pyxel.mouse_x > self.x and pyxel.mouse_x < self.x + self.w and pyxel.mouse_y > self.y and pyxel.mouse_y < self.y + self.h:
            self.on_press()

    def set_on_press(self, on_press):
        self.on_press = on_press


class RenderState(Enum):
    MENU = 1
    LOBBY = 2
    PLAY = 3

class Renderer(object):
    def __init__(self):
        # Generate the course

        # Init pyxel
        pyxel.init(WIDTH, HEIGHT)
        pyxel.mouse(True)

        self.render_state = RenderState.MENU

        # Setup buttons
        self.play_button = Button('Play', 60, 60, 30, 15, 4, 9)
        self.play_button.set_on_press(self.switch_to_lobby)

        self.quit_button = Button('Quit', 170, 60, 30, 15, 4, 9)
        self.quit_button.set_on_press(lambda: pyxel.quit())

    def switch_to_lobby(self):
        self.render_state = RenderState.LOBBY

    def start(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        if not isinstance(self.render_state, RenderState):
            self.render_state = RenderState.MENU

    def draw(self):
        pyxel.cls(7) # Clear screen, set background to white

        if self.render_state is RenderState.MENU:
            # Play button or quit
            pyxel.text(110, 10, 'Slot Racer', 0)
            self.play_button.render()
            self.quit_button.render()
        elif self.render_state is RenderState.LOBBY:
            # Allow users to join a server
            pass
        elif self.render_state is RenderState.PLAY:
            pass

