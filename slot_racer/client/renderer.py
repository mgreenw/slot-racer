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

class Button(object):
    """Simple button for Pyxel. Draws a rectangular button with the given text.

    Button attributes:
    - text: the text to display on the button
    - x: x position of the button
    - y: y position of the button
    - w: width of the button
    - h: height of the button
    - background_color: the background color of the button
    - text_color: the color of the title text of the button
    """
    def __init__(self, text, x, y, w, h, background_color, text_color):
        self.text             = text
        self.x                = x
        self.y                = y
        self.w                = w
        self.h                = h
        self.background_color = background_color
        self.text_color       = text_color
        self.on_press         = None

    def render(self):
        """Render the button and check if the button was pressed. If the
        button has been pressed, run the callback

        """
        pyxel.rect(
            self.x,
            self.y,
            self.x + self.w,
            self.y + self.h,
            self.background_color
        )
        pyxel.text(self.x + 7, self.y + 5, self.text, self.text_color)

        # Check if the button is pressed
        x_in_bounds = self.x < pyxel.mouse_x < self.x + self.w
        y_in_bounds = self.y < pyxel.mouse_y < self.y + self.h
        if self.on_press is not None:
            if pyxel.btn(2000) and x_in_bounds and y_in_bounds:
                self.on_press()

    def set_on_press(self, on_press):
        """Set a callback to run if the button is pressed"""
        self.on_press = on_press


class RenderState(Enum):
    """An enum to keep track of the state of the game"""
    MENU = 1
    COUNTDOWN = 2
    PLAY = 3


class Renderer(object):
    """The main game renderer for the client. Holds the track and client objects

    Renderer attributes:
    - track: the main track object
    - client: the main client object, used for sending and receiving messages
    - stored_trail: an array of points of previous car locations
    - local_car: the car object that is being played by the local player
    - winner: the id of the winning car, if available
    - start_time: the absolute start time of the game relative to this client
    - prev_time: the absolute time of the last frame
    - dt: the timestep between the current frame and the last frame
    - gametime: the running time of the game
    - play_button: the button that users can click to play the game
    - quit_button: a button to quit the game
    """

    def __init__(self, track, client):
        self.track = track
        self.client = client
        self.stored_trail = []
        self.local_car = None
        self.render_state = RenderState.MENU
        self.winner = None

        # Time-specific variables
        self.start_time = None
        self.prev_time = None
        self.dt = 0.0
        self.gametime = 0.0

        # Setup buttons
        self.play_button = Button('Play', 60, 100, 30, 15, 4, 9)
        self.quit_button = Button('Quit', 170, 100, 30, 15, 4, 9)
        self.play_button.set_on_press(lambda: self.client.send('start_game'))
        self.quit_button.set_on_press(lambda: pyxel.quit())

        # Initialize pyxel
        # The width is actually 255 because max pyxel width  is 255,
        # but we will assume it is 256
        pyxel.init(WIDTH - 1 , HEIGHT, fps=30)
        pyxel.mouse(True)  # Use the mouse

    def set_winner(self, winner):
        """Set the winner of the game to the id of the winning car"""
        self.winner = winner

    def switch_to_countdown(self, seconds):
        """Switch the renderer to the countdown"""
        self.render_state = RenderState.COUNTDOWN
        self.synchronized_start = datetime.now() + timedelta(seconds=seconds)

    def switch_to_play(self):
        self.render_state = RenderState.PLAY

    def start(self):
        """Start the renderer given the update and draw methods"""
        pyxel.run(self.update, self.draw)

    def update(self):
        """Update the positions of the cars on the track and check if the local
        should accelerate or stop accelerating.
        """
        # Ensure the renderer state is set
        if not isinstance(self.render_state, RenderState):
            self.render_state = RenderState.MENU

        # Countdown
        if self.render_state is RenderState.COUNTDOWN:
            if datetime.now() > self.synchronized_start:
                self.switch_to_play()
        # Play
        elif self.render_state is RenderState.PLAY:
            now = datetime.now()
            if self.start_time is None:
                self.start_time, self.prev_time = now, now

            # Run time calculations to get gametime
            self.dt = now - self.prev_time
            self.prev_time = now
            self.gametime = (now - self.start_time).total_seconds()

            # Get helper bools for acceleration check
            space_down = pyxel.btn(glfw.KEY_SPACE)
            accelerating = self.local_car.is_accelerating

            # If the car is fallen, check if the explode event needs to be
            # sent to the server
            if self.local_car.fallen:
                if not self.local_car.fallen.sent_to_server:
                    self.local_car.fallen.sent_to_server = True
                    self.client.send(
                        'explode',
                        (self.gametime, 0, self.local_car.distance)
                    )
            # Check for accelerate/decelerate events
            else:
                if space_down and not accelerating:
                    event = self.local_car.accelerate(self.gametime)
                    self.client.send(
                        'accelerate',
                        (self.gametime, event.speed, event.distance)
                    )
                elif not space_down and accelerating:
                    event = self.local_car.stop_accelerating(self.gametime)
                    self.client.send(
                        'stop_accelerating',
                        (self.gametime, event.speed, event.distance)
                    )

            # Update the track using the delta
            self.track.update_all(self.gametime)

    def draw(self):
        """Draw the screen! Using the renderer state, draw the state of the
        game, the cars, and the text
        """
        # Clear screen, set background to off-white
        pyxel.cls(7)

        if self.render_state is RenderState.MENU:
            pyxel.text(110, 10, 'SLOT RACER', 0)
            self.play_button.render()
            self.quit_button.render()

        elif self.render_state is RenderState.COUNTDOWN:
            time = (self.synchronized_start - datetime.now()).total_seconds()
            pyxel.text(30, 30, f'Get Ready! {str(int(time + 1))}', 0)

        elif self.render_state is RenderState.PLAY:
            # Render the track - it is precalculated in the track object
            for (x, y) in self.track.track_0_points[:300]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 3)
            for (x, y) in self.track.track_1_points[:300]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 4)
            for (x, y) in self.track.track_1_points[300:]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 4)
            for (x, y) in self.track.track_0_points[300:]:
                pyxel.rect(x + 128, 72 - y, x + 128, 72 - y, 3)

            # Render the help text in the upper-right of the screen
            pyxel.text(110, 10, 'GO GO GO!', 0)
            pyxel.text(160, 5, 'Press SPACE to', 0)
            pyxel.text(160, 11, 'accelerate. Don\'t', 0)
            pyxel.text(160, 17, 'go too fast, or KABOOM!', 0)

            # Render the trails for the cars, capping it at 20 points total
            self.stored_trail = self.stored_trail[-20:]
            for (x, y) in self.stored_trail:
                pyxel.circ(x, y, 1, 5)

            # Enumerate through and render the cars
            for index, car in enumerate(self.track.participants):
                gametime = self.gametime
                color = 9

                # If the car is a remote car, render it 100 ms in the past
                if self.client.id != index:
                    gametime = self.gametime - 0.1
                    car = car.get_past_car(gametime)
                    color = 11

                # Get the car's position and render it
                # Update the x and y for a new coordinate system
                x, y = car.get_posn()
                x = x + 128
                y = 72 - y
                pyxel.circ(x, y, 2, color)

                # Render the lap number
                lap = math.floor(car.distance) + 1
                pyxel.text(10, 10 * (index + 1), f'{lap}', 0)

                # Add the car's position to the trail
                self.stored_trail.append((x, y))

                # If the car is fallen, render the explode animation!
                if car.fallen:
                    self.explode(x, y, car, gametime)
                    car.speed = 0

            # Render the "winner" text
            if self.winner is None:
                pyxel.text(98, 120, 'First to 10 wins!', 0)
            else:
                if self.winner == self.local_car.id:
                    pyxel.text(110, 120, 'YOU WIN!!!!', 0)
                else:
                    pyxel.text(110, 120, 'You lose :(', 0)

    @staticmethod
    def explode(x, y, car, gametime):
        """Render a car explosion! Use provided images and the derived frame"""
        # Find the time of the explosion
        explosion_time = 1 - (car.fallen.explosion_end - gametime)
        explosion_time = min(max(explosion_time, 0), 1)

        # Get the step of the explosion to render
        step = int(explosion_time * 16)
        w, h = car.fallen.img_sizes[step]

        # Render the explosion image
        pyxel.image(0).load(
            0,
            0,
            f'slot_racer/client/assets/explosion-{step}.png'
        )
        pyxel.blt(x - (w / 2), y - (h / 2), 0, 0, 0, w, h)
