from vector2d import Vector2D


def clamp(n, min, max):
    if n < min:
        return min
    elif n > max:
        return max
    else:
        return n


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
