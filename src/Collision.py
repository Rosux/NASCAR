from math import sqrt

class RectangleCollision:
    def __init__(self, position=(0, 0), width=0, height=0, rotation=0):
        self.position = position
        self.width = width
        self.height = height
        self.rotation = rotation

    def normalize(self, vector):
        norm = sqrt(vector[0] ** 2 + vector[1] ** 2)
        return vector[0] / norm, vector[1] / norm

    def dot(self, vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def edge_direction(self, point0, point1):
        return point1[0] - point0[0], point1[1] - point0[1]

    def orthogonal(self, vector):
        return vector[1], -vector[0]

    def vertices_to_edges(self):
        half_width = self.width / 2
        half_height = self.height / 2
        vertices = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]
        return [self.edge_direction(vertices[i], vertices[(i + 1) % len(vertices)])
                for i in range(len(vertices))]

    def project(self, axis):
        half_width = self.width / 2
        half_height = self.height / 2
        vertices = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]
        dots = [self.dot(vertex, axis) for vertex in vertices]
        return [min(dots), max(dots)]

    def overlap(self, projection1, projection2):
        return min(projection1) <= max(projection2) and \
               min(projection2) <= max(projection1)

    def separating_axis_theorem(self, other):
        edges = self.vertices_to_edges() + other.vertices_to_edges()
        axes = [self.normalize(self.orthogonal(edge)) for edge in edges]

        for axis in axes:
            projection_self = self.project(axis)
            projection_other = other.project(axis)

            overlapping = self.overlap(projection_self, projection_other)

            if not overlapping:
                return False

        return True


if __name__ == "__main__":
