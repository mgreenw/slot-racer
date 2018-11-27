import pyxel
import math

# Define the width and height of the screen
# This makes for a nice 16x9 screen
WIDTH = 255
HEIGHT = 143

def d_to_t(d):
    return (2 * math.pi * d) - (math.pi / 2)

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT)
        self.course = []
        for d in range(0, 51):
            t = d_to_t(d/50)
            a = WIDTH / 2

            sinsqt = math.sin(t) * math.sin(t)
            x = int(round((a * math.cos(t)) / (1 + sinsqt))) + 127
            y = int(round((a * math.sin(t) * math.cos(t)) / (1 + sinsqt))) + 70
            self.course.append((x, y))

        print(self.course)

        pyxel.run(self.update, self.draw)

    def update(self):
        pass



    def draw(self):
        pyxel.cls(7)
        for x, y in self.course:
            pyxel.pix(x, y, 9)

App()
