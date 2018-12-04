import pyxel
import math
from enum import Enum
from datetime import datetime, timedelta

import glfw

from ..game import state, physics

# Define the width and height of the screen
# This makes for a nice 16x9 screen
WIDTH = 256
HEIGHT = 144

# Client-only states
# - Menu
# - Lobby
# - Playing

# Goals
# 1. make the state transitions work
# 2. import the state and begin to work with it
# 3. Look into the websocket stuff

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
    COUNTDOWN = 4


class Renderer(object):
    def __init__(self, track, client):
        self.client = client
        self.track = track
        self.stored = []
        self.local_car = None

        # Init pyxel
        # Weird case because max width is 255, but we will assume it is 256
        pyxel.init(WIDTH - 1 , HEIGHT, fps=30)
        pyxel.mouse(True)

        self.render_state = RenderState.MENU

        # Setup buttons
        self.play_button = Button('Play', 60, 60, 30, 15, 4, 9)
        # self.play_button.set_on_press(self.switch_to_countdown())

        self.quit_button = Button('Quit', 170, 60, 30, 15, 4, 9)
        self.quit_button.set_on_press(lambda: pyxel.quit())

        self.start_time = None
        self.prev_time = None
        self.dt = 0.0
        self.game_time = 0.0

    def switch_to_lobby(self):
        self.render_state = RenderState.LOBBY

    def switch_to_countdown(self, time_to_start):
        self.render_state = RenderState.COUNTDOWN
        self.synchronized_start = datetime.now() + timedelta(seconds=time_to_start)

    def switch_to_play(self):
        self.render_state = RenderState.PLAY

    def start(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        if not isinstance(self.render_state, RenderState):
            self.render_state = RenderState.MENU

        if self.render_state is RenderState.MENU:
            if pyxel.btn(glfw.KEY_ENTER):
                self.client.send('start_game')
        elif self.render_state is RenderState.PLAY:

            now = datetime.now()
            if self.start_time is None:
                self.start_time = now
                self.prev_time = now

            self.dt = now - self.prev_time
            self.prev_time = now
            self.game_time = (now - self.start_time).total_seconds()

            space_down = pyxel.btn(glfw.KEY_SPACE)
            accelerating = self.local_car.is_accelerating

            if self.local_car.fallen:
                if not self.local_car.fallen.sent_to_server:
                    self.local_car.fallen.sent_to_server = True
                    self.client.send('explode', (self.game_time, 0, self.local_car.distance))
            else:
                if space_down and not accelerating:
                    event = self.local_car.accelerate(self.game_time)
                    self.client.send('accelerate', (self.game_time, event.speed, event.distance))
                elif not space_down and accelerating:
                    event = self.local_car.stop_accelerating(self.game_time)
                    self.client.send('stop_accelerating', (self.game_time, event.speed, event.distance))

                # Update the track using the delta
            self.track.update_all(self.game_time)
        elif self.render_state is RenderState.COUNTDOWN:
            if datetime.now() > self.synchronized_start:
                self.switch_to_play()

    def draw(self):
        pyxel.cls(7) # Clear screen, set background to white

        if self.render_state is RenderState.MENU:
            # Play button or quit
            pyxel.text(110, 10, 'SLOT RACER', 0)
            self.play_button.render()
            self.quit_button.render()
        elif self.render_state is RenderState.LOBBY:
            pyxel.text(110, 10, 'JOIN A GAME', 0)
            # Allow users to join a server
            pass
        elif self.render_state is RenderState.PLAY:

            for (x, y) in self.track.track_0_points[:300]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 3)

            for (x, y) in self.track.track_1_points[:300]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 4)

            for (x, y) in self.track.track_1_points[300:]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 4)

            for (x, y) in self.track.track_0_points[300:]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 3)

            pyxel.text(110, 10, 'GO GO GO!', 0)

            for (x, y) in self.stored:
                pyxel.circ(x, y, 1, 5)

            gametime = self.game_time

            for index, car in enumerate(self.track.participants):
                x, y = 0, 0
                color = 9
                if self.client.id != index:
                    gametime = self.game_time - 0.1
                    car = car.get_past_car(gametime)
                    color = 11
                x, y = car.get_posn()

                x = x + 128
                y = 72 - y
                self.stored.append((x, y))
                pyxel.circ(x, y, 2, color)
                pyxel.text(10, 10 * (index + 1), f'{car.speed}', 0)
                if car.fallen:
                    self.explode(x, y, car, gametime)
                    car.speed = 0

            self.stored = self.stored[-20:]

        elif self.render_state is RenderState.COUNTDOWN:
            time = (self.synchronized_start - datetime.now()).total_seconds()
            pyxel.text(30, 30, f'Get Ready! {str(int(time + 1))}', 0)

    def explode(self, x, y, car, gametime):
        explosion_time = min(max(1 - (car.fallen.explosion_end - gametime), 0), 1)
        step = int(explosion_time * 16)
        w, h = car.fallen.img_sizes[step]
        pyxel.image(0).load(0, 0, f'slot_racer/client/explosion-{step}.png')
        pyxel.blt(x - (w / 2), y - (h / 2), 0, 0, 0, w, h)
