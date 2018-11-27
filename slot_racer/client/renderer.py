import pyxel
import math

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

def d_to_t(d):
    return (2.0 * math.pi * d) - (math.pi / 2.0)

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

class Renderer(object):
    def __init__(self):
        # Generate the course
        self.course_1 = []
        for d in range(0, 51):
            t = d_to_t(d / 50.0)
            a = WIDTH / 2
            sinsqt = math.sin(t) * math.sin(t)
            x = int(round((a * math.cos(t)) / (1 + sinsqt))) + 127
            y = int(round((a * math.sin(t) * math.cos(t)) / (1 + sinsqt))) + 70
            self.course_1.append((x, y))

        self.course_2 = []
        for d in range(0, 51):
            t = d_to_t(d + 0.5 / 50.0)
            a = WIDTH / 2
            sinsqt = math.sin(t) * math.sin(t)
            x = int(round((a * math.cos(t)) / (1 + sinsqt))) + 127
            y = int(round((a * math.sin(t) * math.cos(t)) / (1 + sinsqt))) + 70
            self.course_2.append((x, y))


        # Init pyxel
        pyxel.init(WIDTH, HEIGHT)
        pyxel.mouse(True)

        # Setup buttons
        self.play_button = Button('Play', 60, 60, 30, 15, 4, 9)
        self.play_button.set_on_press(lambda: print('play pressed'))

        self.quit_button = Button('Quit', 170, 60, 30, 15, 4, 9)
        self.quit_button.set_on_press(lambda: pyxel.quit())

    def start(self):
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(7) # Clear screen, set background to white
        course = None
        if pyxel.frame_count % 30 < 15:
            course = self.course_1
        else:
            course = self.course_2
        for x, y in course:
            pyxel.pix(x, y, 9)
        pyxel.text(110, 10, 'Slot Racer', 0)
        self.play_button.render()
        self.quit_button.render()
