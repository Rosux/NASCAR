from enum import Enum
from vector2d import Vector2D
from math import sqrt, cos, sin, radians
from Utils import RotateVector, RotateVectorAroundPoint
import sys


class Direction(Enum):
    NONE = -1
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

class RectangleCollision:
    def __init__(self, position=Vector2D(0, 0), width=0, height=0, rotation=0):
        self.position = Vector2D(position.x, position.y)
        self.width = width
        self.height = height
        self.rotation = radians(rotation) # in radians

    def UpdatePositions(self, position, rotation):
        self.position = Vector2D(position.x, position.y)
        self.rotation = rotation

    def Normalize(self, vector):
        norm = sqrt(vector.x ** 2 + vector.y ** 2)
        if norm == 0:
            return Vector2D(0, 0)
        return Vector2D(vector.x / norm, vector.y / norm)

    def Dot(self, vector1, vector2):
        return vector1.x * vector2.x + vector1.y * vector2.y
    
    def RotatePoint(self, point, angle):
        x_rot = point.x * cos(angle) - point.y * sin(angle)
        y_rot = point.x * sin(angle) + point.y * cos(angle)
        return Vector2D(x_rot, y_rot)
    
    def GetPoints(self, rect):
        halfWidth = rect.width/2
        halfHeight = rect.height/2
        return [
            rect.position + RotateVector(Vector2D(-halfWidth, halfHeight), rect.rotation, True),
            rect.position + RotateVector(Vector2D(halfWidth, halfHeight), rect.rotation, True),
            rect.position + RotateVector(Vector2D(halfWidth, -halfHeight), rect.rotation, True),
            rect.position + RotateVector(Vector2D(-halfWidth, -halfHeight), rect.rotation, True),
        ]

    def CheckCollision(self, other):
        selfPoints = self.GetPoints(self)
        otherPoints = self.GetPoints(other)
        
        for i in range(2):
            if i == 1:
                otherPoints, selfPoints = selfPoints, otherPoints
            for a in range(len(selfPoints)):
                b = (a + 1) % len(selfPoints)
                axisProjection = Vector2D(-(selfPoints[b].y - selfPoints[a].y), selfPoints[b].x - selfPoints[a].x)
                axisProjection = self.Normalize(axisProjection)
                
                minRange1 = sys.maxsize
                maxRange1 = -sys.maxsize - 1
                for p in range(len(selfPoints)):
                    q = self.Dot(Vector2D(selfPoints[p].x, selfPoints[p].y), axisProjection)
                    minRange1 = min(minRange1, q)
                    maxRange1 = max(maxRange1, q)
                    
                minRange2 = sys.maxsize
                maxRange2 = -sys.maxsize - 1
                for p in range(len(otherPoints)):
                    q = self.Dot(Vector2D(otherPoints[p].x, otherPoints[p].y), axisProjection)
                    minRange2 = min(minRange2, q)
                    maxRange2 = max(maxRange2, q)
                    
                if not (maxRange2 >= minRange1 and maxRange1 >= minRange2):
                    return False

        return True
    
    def VerticesInsideOtherShape(self, other):
        if not hasattr(other, "collider") and not self.CheckCollision(other.collider):
            return []
        otherCollider = other.collider
        rotationFactor = -self.rotation
        # get points
        selfAABB = self.GetPoints(self)
        otherAABB = self.GetPoints(otherCollider)
        # rotate points around self origin
        for i in range(4):
            selfAABB[i] = RotateVectorAroundPoint(selfAABB[i], self.position, rotationFactor, True)
            otherAABB[i] = RotateVectorAroundPoint(otherAABB[i], self.position, rotationFactor, True)
        tl = self.position + Vector2D(-self.width/2, -self.height/2)
        br = self.position + Vector2D(self.width/2, self.height/2)
        # AABB check for each vertex on the other shape
        points = []
        for i in range(4):
            if otherAABB[i].x >= tl.x and otherAABB[i].x <= br.x and otherAABB[i].y >= tl.y and otherAABB[i].y <= br.y:
                points.append(RotateVectorAroundPoint(otherAABB[i], self.position, -rotationFactor, True))
        
        for p in points:
            r = RotateVectorAroundPoint(p, self.position, rotationFactor + radians(45), True)
            dir = Direction.NONE
            if r.x <= self.position.x and r.y <= self.position.y: # Bottom
                print("Bottom")
                dir = Direction.BOTTOM
            elif r.x <= self.position.x and r.y >= self.position.y: # Left
                print("Left")
                dir = Direction.LEFT
            elif r.x >= self.position.x and r.y <= self.position.y: # Top
                print("Top")
                dir = Direction.TOP
            elif r.x >= self.position.x and r.y >= self.position.y: # Right
                print("Right")
                dir = Direction.RIGHT
            # push rigidbody away from collider
            if hasattr(other, "rb"):
                distance = Vector2D(0, 0)
                if dir == Direction.RIGHT:
                    vv = Vector2D(p.x - self.position.x, 0) * other.rb.mass
                    distance = RotateVector(vv, -rotationFactor, True)
                if dir == Direction.LEFT:
                    vv = Vector2D(-(p.x - self.position.x), 0) * other.rb.mass
                    distance = RotateVector(vv, -rotationFactor + radians(180), True)
                if dir == Direction.TOP:
                    vv = Vector2D(0, -(p.y - self.position.y)) * other.rb.mass
                    distance = RotateVector(vv, -rotationFactor + radians(180), True)
                if dir == Direction.BOTTOM:
                    vv = Vector2D(0, (p.y - self.position.y)) * other.rb.mass
                    distance = RotateVector(vv, -rotationFactor, True)
                other.rb.velocity = Vector2D(0, 0)
                other.rb.AddForceAtPosition(distance, p)
            
            
        return points


if __name__ == "__main__":
    a = RectangleCollision(Vector2D(0, 0), 1, 1, 0)
    b = RectangleCollision(Vector2D(1, 1), 1, 1, 0)
    c = RectangleCollision(Vector2D(1, 1), 0.999999, 0.999999, 0)
    print(f"""
A should intersect with B but not with C:
A check with B (True expected) = {a.CheckCollision(b)}
A check with C (False expected) = {a.CheckCollision(c)}
""")