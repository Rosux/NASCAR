from vector2d import Vector2D
from Entity import Entity
from Collision import RectangleCollision
import math

class Wall(Entity):
    def __init__(self, position: Vector2D=Vector2D(0, 0), width: float = 1, height: float = 1, rotation: float = 0):
        super().__init__()
        self.collider = RectangleCollision(position, width, height, rotation)
