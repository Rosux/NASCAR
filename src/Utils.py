from vector2d import Vector2D
import math


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


def Dot(v1, v2):
    return v1.x * v2.x + v1.y * v2.y


def clampVector(vector, minX, maxX, minY, maxY):
    return Vector2D(
        clamp(vector.x, minX, maxX),
        clamp(vector.y, minY, maxY)
    )


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


def Magnitude(p1):  
    return math.sqrt(p1.x**2 + p1.y**2)


def RotateVector(p1, angle, radians=False):
    if not radians:
        radians = math.radians(angle)
    else:
        radians = angle
    return Vector2D(p1.x * math.cos(radians) - p1.y * math.sin(radians), p1.x * math.sin(radians) + p1.y * math.cos(radians))


def RotateVectorAroundPoint(vector, pivot, angle, radians=False):
    if not radians:
        radians = math.radians(angle)
    else:
        radians = angle

    translated_vector = Vector2D(vector.x - pivot.x, vector.y - pivot.y)

    rotated_x = translated_vector.x * math.cos(radians) - translated_vector.y * math.sin(radians)
    rotated_y = translated_vector.x * math.sin(radians) + translated_vector.y * math.cos(radians)

    rotated_vector = Vector2D(rotated_x, rotated_y)

    # Translate the vector back to its original position
    rotated_vector.x += pivot.x
    rotated_vector.y += pivot.y

    return rotated_vector

