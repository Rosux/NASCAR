from vector2d import Vector2D
from math import sqrt, cos, sin, radians
import sys

class RectangleCollision:
    def __init__(self, position=Vector2D(0, 0), width=0, height=0, rotation=0):
        self.position = Vector2D(position.x, position.y)
        self.width = width
        self.height = height
        self.rotation = rotation

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
            rect.position + self.RotatePoint(Vector2D(halfWidth, halfHeight), radians(rect.rotation)),
            rect.position - self.RotatePoint(Vector2D(halfWidth, halfHeight), radians(rect.rotation)),
            rect.position + self.RotatePoint(Vector2D(halfWidth, -halfHeight), radians(rect.rotation)),
            rect.position - self.RotatePoint(Vector2D(-halfWidth, halfHeight), radians(rect.rotation)),
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

if __name__ == "__main__":
    a = RectangleCollision(Vector2D(0, 0), 1, 1, 0)
    b = RectangleCollision(Vector2D(1, 1), 1, 1, 0)
    c = RectangleCollision(Vector2D(1, 1), 0.999999, 0.999999, 0)
    print(f"""
A should intersect with B but not with C:
A check with B (True expected) = {a.CheckCollision(b)}
A check with C (False expected) = {a.CheckCollision(c)}
""")