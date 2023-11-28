import numpy as np


class Cube:
    def __init__(self, center, size, texture):
        self.center = center
        self.size = size
        self.points = self.generate_points()
        self.texture = texture

    def generate_points(self):
        half_size = self.size / 2
        points = np.array([
            [-1, -1, -1, 1],
            [1, -1, -1, 1],
            [1, 1, -1, 1],
            [-1, 1, -1, 1],
            [-1, -1, 1, 1],
            [1, -1, 1, 1],
            [1, 1, 1, 1],
            [-1, 1, 1, 1]
        ]).T
        transform_matrix = np.array([
            [half_size, 0, 0, self.center[0]],
            [0, half_size, 0, self.center[1]],
            [0, 0, half_size, self.center[2]]
        ])
        return np.dot(transform_matrix, points).T
