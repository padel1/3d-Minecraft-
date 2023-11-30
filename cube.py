import numpy as np


class Cube:
    def __init__(self, center, size, texture):
        self.center = np.array(center)
        self.size = size
        self.points = self.generate_points()
        self.texture = texture
        self.min_bound = self.center - np.array([size / 2, size / 2, size / 2])
        self.max_bound = self.center + np.array([size / 2, size / 2, size / 2])

    def generate_points(self):
        half_size = self.size / 2
        points = np.array(
            [
                [-1, -1, -1, 1],
                [1, -1, -1, 1],
                [1, 1, -1, 1],
                [-1, 1, -1, 1],
                [-1, -1, 1, 1],
                [1, -1, 1, 1],
                [1, 1, 1, 1],
                [-1, 1, 1, 1],
            ]
        ).T
        transform_matrix = np.array(
            [
                [half_size, 0, 0, self.center[0]],
                [0, half_size, 0, self.center[1]],
                [0, 0, half_size, self.center[2]],
            ]
        )
        return np.dot(transform_matrix, points).T

    def contains_point(self, point):
        return all(self.min_bound <= point) and all(point <= self.max_bound)

    def ray_intersection(self, origin, direction):
        t_values = []

        for i in range(3):
            if direction[i] != 0:
                t1 = (self.min_bound[i] - origin[i]) / direction[i]
                t2 = (self.max_bound[i] - origin[i]) / direction[i]
                t_values.extend([t1, t2])

        t_values.sort()

        for t in t_values:
            intersection_point = origin + t * direction
            if self.contains_point(intersection_point):
                return intersection_point

        return None


