import pygame
from vector2d import Vector2D

class Entity:
    game = None

    @classmethod
    def SetGame(cls, game):
        cls.game = game

    def __init__(self):
        self.id = id(self)
        self.active = True
        self.collision = True

    def Update(self, deltaTime, events):
        # this runs each frame
        if Entity.game is not None:
            pass