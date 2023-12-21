import math
import numpy as np

from settings import CUBE_SIZE
# cubes functions:


def rectangle_center(points):
    points_array = np.array(points)
    center = np.mean(points_array, axis=0)
    return center


def get_surfaces(pts):
    arr = [
        # z
        ["front", [[4, pts[4]], [5, pts[5]], [6, pts[6]], [7, pts[7]]]],
        ["back", [[0, pts[1]], [1, pts[0]], [2, pts[3]], [3, pts[2]]]],
        # y
        ["top", [[0, pts[0]], [1, pts[1]], [5, pts[5]], [4, pts[4]]]],
        ["down", [[2, pts[2]], [3, pts[3]], [7, pts[7]], [6, pts[6]]]],
        # x
        ["left", [[5, pts[1]], [1, pts[2]], [2, pts[6]], [6, pts[5]]]],
        ["right", [[4, pts[3]], [0, pts[0]], [3, pts[4]], [7, pts[7]]]],
    ]

    return sorted(
        arr,
        key=lambda x: np.sqrt(
            np.sum((rectangle_center([p[1] for p in x[1]])) ** 2)),
        reverse=True,
    )


def get_sorted_cubes(cubes, camera_position):
    for cube in cubes:
        
        cube.center = np.mean(cube.points, axis=0)
    return sorted(
        cubes,
        key=lambda cube: np.linalg.norm(
            np.array(cube.center) - camera_position
        ),
        reverse=True,
    )

# points functions:


def transform_points(points, f):
    points_x = points[..., 0]
    points_y = points[..., 1]
    points_z = points[..., 2] - f + 0.0001

    return np.column_stack(
        (points_x / points_z, points_y / points_z, np.ones(len(points)))
    )

def rotate_matrix_z(theta):
    return np.array(
        [
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )


def rotate_matrix_x(theta):
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)],
        ]
    )


def rotate_matrix_y(theta):
    return np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )


# ground functions:
# colors = [(255, 255, 255),
#           (255, 0, 0),
#           (0, 255, 0),
#           (0, 0, 255),
#           (255, 255, 0),
#           (255, 0, 255),
#           ]


def generate_ground(grid_size=20, step_size=CUBE_SIZE):
    ground = []
    for i in range(-grid_size // 2, grid_size // 2):
        for j in range(-grid_size // 2, grid_size // 2):
            points = np.array(
                [
                    [i * step_size, 2, j * step_size],
                    [(i + 1) * step_size, 2, j * step_size],
                    [(i + 1) * step_size, 2, (j + 1) * step_size],
                    [i * step_size, 2, (j + 1) * step_size],
                ]
            )
            ground.append(points)

    return np.array(ground)

# lighting functions:


def normalize_value(value, min_value, max_value):
    new_min = 0
    new_max = 1.0
    normalized_value = (value - min_value) / (max_value - min_value) * (
        new_max - new_min
    ) + new_min
    return normalized_value


def Dot_product(vec1, vec2):
    return np.dot(vec1, vec2)


def simulate_sunlight(surface_points, sun_center):
    surface_normal = np.cross(
        surface_points[1] - surface_points[0],
        surface_points[2] - surface_points[0],
    )
    surface_normal /= np.linalg.norm(surface_normal)

    light_direction = sun_center - np.mean(surface_points, axis=0)
    light_direction /= np.linalg.norm(light_direction)
    dot_product = Dot_product(surface_normal, light_direction)
    intensity = normalize_value(dot_product, -1, 1)
    return intensity


def ray_plane_intersection(ray_origin, ray_direction, plane_normal, plane_point):
    d = -np.dot(plane_normal, plane_point)
    t = -(np.dot(plane_normal, ray_origin) + d) / \
        np.dot(plane_normal, ray_direction)

    intersection_point = ray_origin + t * ray_direction

    return intersection_point


def point_in_polygon(point, polygon):
    x, _, y = point
    n = len(polygon)
    inside = False

    for i in range(n):
        x1, _, y1 = polygon[i]
        x2, _, y2 = polygon[(i + 1) % n]

        # Check if the point is on the edge
        if (y1 <= y < y2) or (y2 <= y < y1):
            if x1 + (y - y1) / (y2 - y1) * (x2 - x1) > x:
                inside = not inside

    return inside
