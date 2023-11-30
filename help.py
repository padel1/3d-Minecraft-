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
        [[0, pts[1]], [1, pts[0]], [2, pts[3]], [3, pts[2]]],

        [[4, pts[4]], [5, pts[5]], [6, pts[6]], [7, pts[7]]],
        # y
        [[0, pts[0]], [1, pts[1]], [5, pts[5]], [4, pts[4]]],
        [[2, pts[2]], [3, pts[3]], [7, pts[7]], [6, pts[6]]],
        # x
        [[1, pts[1]], [2, pts[2]], [6, pts[6]], [5, pts[5]]],
        [[0, pts[3]], [3, pts[0]], [7, pts[4]], [4, pts[7]]],
    ]

    return sorted(
        arr,
        key=lambda x: np.sqrt(
            np.sum((rectangle_center([p[1] for p in x])) ** 2)),
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
colors = [(255, 255, 255),
          (255, 0, 0),
          (0, 255, 0),
          (0, 0, 255),
          (255, 255, 0),
          (255, 0, 255),
          ]


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


# # Add a new method to your Scene class
# def get_ground_intersection(self, ray_direction):
#     for i, polygon in enumerate(self.ground):
#         transformed_points = transform_points(
#             polygon - self.camera.position, self.camera.f)
 

#         # Check if the ray intersects with the ground polygon
#         if self.is_ray_intersects_polygon(ray_direction, transformed_points):
#             # Find the intersection point
#             intersection_point = ray_plane_intersection(
#                 self.camera.position, ray_direction,
#                 np.cross(transformed_points[1] - transformed_points[0],
#                          transformed_points[2] - transformed_points[0]),
#                 transformed_points[0]
#             )
#             return intersection_point

#     return None

# # Add another helper method


# def is_ray_intersects_polygon(self, ray_direction, polygon_points):
#     # Assuming polygon_points is in 3D, and the ray is a vector in the same space
#     v0, v1, v2 = polygon_points

#     # Calculate the normal of the polygon
#     normal = np.cross(v1 - v0, v2 - v0)

#     # Check if the ray is parallel to the plane of the polygon
#     if np.dot(normal, ray_direction) == 0:
#         return False

#     # Check if the ray intersects the plane of the polygon
#     d = -np.dot(normal, v0)
#     t = -(np.dot(normal, self.camera.position) + d) / \
#         np.dot(normal, ray_direction)

#     # Check if the intersection point is inside the polygon
#     intersection_point = self.camera.position + t * ray_direction

#     u = np.dot(np.cross(v1 - v0, intersection_point - v0), normal)
#     v = np.dot(np.cross(v2 - v1, intersection_point - v1), normal)
#     w = np.dot(np.cross(v0 - v2, intersection_point - v2), normal)

#     return all(0 <= val <= 1 for val in [u, v, w])


def get_ground_intersection(self, ray_direction):
    for i, polygon in enumerate(self.ground):
        transformed_points = transform_points(polygon - self.camera.position, self.camera.f)
        points_2d = np.dot(self.camera.K, transformed_points.T).T

        # Check if the ray intersects with the ground polygon
        intersection_point, intersected_polygon = self.get_intersection_info(ray_direction, transformed_points)

        if intersection_point is not None:
            return intersection_point, intersected_polygon

    return None, None

def get_intersection_info(self, ray_direction, polygon_points):
    # Assuming polygon_points is in 3D, and the ray is a vector in the same space
    v0, v1, v2 = polygon_points

    # Calculate the normal of the polygon
    normal = np.cross(v1 - v0, v2 - v0)

    # Check if the ray is parallel to the plane of the polygon
    if np.dot(normal, ray_direction) == 0:
        return None, None

    # Check if the ray intersects the plane of the polygon
    d = -np.dot(normal, v0)
    t = -(np.dot(normal, self.camera.position) + d) / np.dot(normal, ray_direction)

    # Check if the intersection point is inside the polygon
    intersection_point = self.camera.position + t * ray_direction

    u = np.dot(np.cross(v1 - v0, intersection_point - v0), normal)
    v = np.dot(np.cross(v2 - v1, intersection_point - v1), normal)
    w = np.dot(np.cross(v0 - v2, intersection_point - v2), normal)

    if all(0 <= val <= 1 for val in [u, v, w]):
        intersected_polygon = polygon_points
        return intersection_point, intersected_polygon

    return None, None
