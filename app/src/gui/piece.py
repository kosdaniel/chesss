"""
Module for the Piece class
"""

import pygame as pg
from app import config as cf

class Piece(pg.sprite.Sprite):
    """
    Class for representing a single chess piece as a pygame Sprite
    """
    def __init__(self, type: str, width: int, height: int):
        """
        Loads its own sprite image from the respective file based on its type and color
        """
        pg.sprite.Sprite.__init__(self)

        self.width = width
        self.height = height
        if type not in cf.IMAGE_PATHS.keys():
            raise ValueError('Invalid piece type argument')
        self.type = type

        self.image = pg.image.load(cf.IMAGE_PATHS[type]).convert_alpha()
        self.image = pg.transform.smoothscale(self.image, (self.width, self.height))

        self.rect = self.image.get_rect()


    def render(self, x: int, y: int, surface: pg.Surface, center: bool = False):
        """
        Renders itself onto the arg surface on the given coordinates. Takes the coordinates
        as the bottom left corner of the target rect if center is false, else takes the 
        coordinates as the center of the target rect
        """
        if not center:
            self.rect.bottomleft = (x, y)
        else:
            self.rect.center = (x, y)
        surface.blit(self.image, self.rect)
        
