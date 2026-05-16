from asrc.utilities import draw_image
from asrc.constants import *

class Square:
    #AG [type refers to type of square {normal, mine, flag, hint}
    def __init__(self, row, col, type, image):
        self.row = row
        self.col = col
        self.type = type
        self.image = image

    def draw(self, cell_size):
        if self.type == "Normal":
            draw_image(window, self.image, (self.col, self.row), 0, cell_size)
        elif self.type == "Mine":
            draw_image(window, self.image, (self.col, self.row), 0, cell_size)
        else:
            draw_image(window, self.image, (self.col, self.row), 0, cell_size)

    def getRow(self):
        return self.row

    def getCol(self):
        return self.col