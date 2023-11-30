import math
import pygame
import sys
import numpy as np
from settings import *
from cube import *
from camera import *
from texture import *
from help import *


class Scene:
    def __init__(self):
        pygame.init()
        # inventory bar
        self.inventory_bar_position = (half_width -
                                       gui["inventory"].get_width()//2, screen_height - screen_height//5)
        self.texture_slot_size = 45
        self.textures_per_row = 9
        self.selected_texture_index = 0

        #
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.camera = Camera()
        self.clock = pygame.time.Clock()
        # cubes
        self.cubes = [Cube((78, -150, -15), 0.3, textures8["sand"]),]

        # move
        self.acceleration = 0
        self.x = 0
        self.sensitivity = 0.005
        self.sound = Sound()

        # ground
        self.ground = generate_ground()
        self.ground_under_player = -2
        # tools
        self.scene = Scenes.loading
        self.add_cubes_sound = None

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        is_inside_cube = any(
            cube.center[1] - cube.size / 2
            < self.camera.position[1] + 5
            < cube.center[1] + cube.size / 2
            and cube.center[0] - cube.size / 2
            < self.camera.position[0]
            < cube.center[0] + cube.size / 2
            and cube.center[2] - cube.size / 2
            < self.camera.position[2]
            < cube.center[2] + cube.size / 2
            for cube in self.cubes
        )
        if is_inside_cube:
            self.camera.position[1] = -8
            self.ground_under_player = self.camera.position[1]
        else:
            self.ground_under_player = -2

        mouse_rel = pygame.mouse.get_rel()
        pygame.mouse.set_pos(half_width, half_height)
        self.camera.angle_h += self.sensitivity * mouse_rel[0]
        self.camera.angle_v += self.sensitivity * (-mouse_rel[1])
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_SPACE]:
            pass

        if keys[pygame.K_p]:
            pygame.mouse.set_visible(True)
        if keys[pygame.K_g]:
            self.x += 2

        if keys[pygame.K_h]:
            self.x -= 2
        if keys[pygame.K_1]:
            self.camera.position = [-35, -2, -25]
            self.camera.angle_h = 30
        if keys[pygame.K_2]:
            self.camera.position = [+64, -2, -25]
        if keys[pygame.K_3]:
            self.camera.position = [89, -2, +25]

        # movement
        if keys[pygame.K_a]:
            new_position = self.camera.position.copy()
            new_position[2] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            new_position[0] -= MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            if not self.check_collision(new_position):

                self.camera.position = new_position
        if keys[pygame.K_d]:
            self.camera.position[2] -= MOVEMENT_SPEED * \
                np.sin(self.camera.angle_h)
            self.camera.position[0] += MOVEMENT_SPEED * \
                np.cos(self.camera.angle_h)
        if keys[pygame.K_w]:
            # self.camera.position[2] += MOVEMENT_SPEED * \
            #     np.cos(self.camera.angle_h)
            # self.camera.position[0] += MOVEMENT_SPEED * \
            #     np.sin(self.camera.angle_h)

            new_position = self.camera.position.copy()
            new_position[2] += MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            new_position[0] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)

            if not self.check_collision(new_position):
                # print("dkhal")
                self.camera.position = new_position
            # print(self.camera.position)
            # self.sound.walk.play()
        if keys[pygame.K_s]:
            self.camera.position[2] -= MOVEMENT_SPEED * \
                np.cos(self.camera.angle_h)
            self.camera.position[0] -= MOVEMENT_SPEED * \
                np.sin(self.camera.angle_h)

        if keys[pygame.K_r]:
            self.cubes = initial_cubes
        if keys[pygame.K_q]:
            self.camera.position[1] -= 2
        if keys[pygame.K_e]:
            self.camera.position[1] += MOVEMENT_SPEED
        if keys[pygame.K_LEFT]:
            self.selected_texture_index -= 1
            pygame.time.delay(100)
        if keys[pygame.K_RIGHT]:
            self.selected_texture_index += 1
            pygame.time.delay(100)

        if self.camera.position[1] < self.ground_under_player:
            self.acceleration += 0.09
            self.camera.position[1] += self.acceleration
        else:
            self.acceleration = 0

    def check_collision(self, new_position):
        player_point = np.array(
            [new_position[0], new_position[1], new_position[2]])

        player_width = 0.5
        player_height = 2.5

        for cube in self.cubes:
            cube_center = np.array(cube.center)
            cube_size = cube.size

            if (
                cube_center[0] - cube_size < player_point[0] + player_width
                and cube_center[0] + cube_size > player_point[0] - player_width
                and cube_center[1] - cube_size < player_point[1] + player_height
                and cube_center[1] + cube_size > player_point[1] - player_height
                and cube_center[2] - cube_size < player_point[2] + player_width
                and cube_center[2] + cube_size > player_point[2] - player_width
            ):
                print("Collision detected!")
                return True

        print("No collision.")
        return False

    def draw_ground(self, rotate_h, rotate_v):

        for i, polygon in enumerate(self.ground):

            new_points = polygon - self.camera.position
            transformed_points = np.dot(new_points, rotate_h)
            transformed_points = np.dot(transformed_points, rotate_v)
            tra = transformed_points
            transformed_points = transform_points(
                transformed_points, self.camera.f)
            points_2d = np.dot(self.camera.K, transformed_points.T).T
            at_least_one_point_in_view = any(
                0 <= point[0] < screen_width and 0 <= point[1] < screen_height for point in points_2d
            )

            if at_least_one_point_in_view and all(
                point[-1] > self.camera.f for point in tra
            ):
                if i == 20 or i == 30 or i == 44:
                    pygame.draw.polygon(
                        self.screen, (255, 255, 255), points_2d)
                else:
                    pygame.draw.polygon(
                        self.screen, (np.round(255-i/2), np.round(i / 2)//2, 5), points_2d)
                # draw_polygon(self.screen, points_2d, pygame.image.load(
                #     r"assets\bedrock.png"), 1)
    # Add a new method to your Scene class

    def get_ground_intersection(self, ray_direction):
        for polygon in enumerate(self.ground):

            # Check if the ray intersects with the ground polygon
            if self.is_ray_intersects_polygon(ray_direction, polygon[1]):
                # Find the intersection point
                intersection_point = ray_plane_intersection(
                    self.camera.position, ray_direction,
                    np.cross(polygon[1][1] - polygon[1][0],
                             polygon[1][2] - polygon[1][0]),
                    polygon[1][0]
                )
                return intersection_point

        return None

    def is_ray_intersects_polygon(self, ray_direction, polygon_points):
        # Assuming polygon_points is in 3D, and the ray is a vector in the same space
        v0, v1, v2, v4 = polygon_points

        # Calculate the normal of the polygon
        normal = np.cross(v1 - v0, v2 - v0)

        # Check if the ray is parallel to the plane of the polygon
        if np.dot(normal, ray_direction) == 0:
            return False

        # Check if the ray intersects the plane of the polygon
        d = -np.dot(normal, v0)
        t = -(np.dot(normal, self.camera.position) + d) / \
            np.dot(normal, ray_direction)

        # Check if the intersection point is inside the polygon
        intersection_point = self.camera.position + t * ray_direction

        u = np.dot(np.cross(v1 - v0, intersection_point - v0), normal)
        v = np.dot(np.cross(v2 - v1, intersection_point - v1), normal)
        w = np.dot(np.cross(v0 - v2, intersection_point - v2), normal)

        # return all(0 <= val <= 1 for val in [u, v, w])
        return True

    def get_intersection_cube(self, origin, direction):
        for cube in self.cubes:
            intersection_point = cube.ray_intersection(origin, direction)
            if intersection_point is not None:
                print("'hi'")
                return cube
        return None

    def render_inventory_bar(self):

        current_x, current_y = self.inventory_bar_position
        y = current_y + 10
        x = current_x + 10
        for i in range(self.textures_per_row):

            texture_image = pygame.transform.scale(
                list(textures8.values())[i], (30, 30))
            self.screen.blit(texture_image, (x, y))

            if i == self.selected_texture_index:
                self.screen.blit(gui["hover_slot"], (current_x, current_y))

            x += self.texture_slot_size - 1
            current_x += self.texture_slot_size - 1

            # Move to the next row after reaching the maximum number of textures per row
            # if (i + 1) % self.textures_per_row == 0:
            #     current_x = self.inventory_bar_position[0]
            #     current_y += self.texture_slot_size
    # def get_ground_intersection(self, ray_direction):
    #     for i, polygon in enumerate(self.ground):
    #         transformed_points = transform_points(polygon - self.camera.position, self.camera.f)
    #         points_2d = np.dot(self.camera.K, transformed_points.T).T

    #         # Check if the ray intersects with the ground polygon
    #         intersection_point, intersected_polygon = self.get_intersection_info(ray_direction, transformed_points)

    #         if intersection_point is not None:
    #             return intersection_point, intersected_polygon

    #     return None, None

    # def get_intersection_info(self, ray_direction, polygon_points):
    #     # Assuming polygon_points is in 3D, and the ray is a vector in the same space
    #     v0, v1, v2,v4 = polygon_points

    #     # Calculate the normal of the polygon
    #     normal = np.cross(v1 - v0, v2 - v0)

    #     # Check if the ray is parallel to the plane of the polygon
    #     if np.dot(normal, ray_direction) == 0:
    #         return None, None

    #     # Check if the ray intersects the plane of the polygon
    #     d = -np.dot(normal, v0)
    #     t = -(np.dot(normal, self.camera.position) + d) / np.dot(normal, ray_direction)

    #     # Check if the intersection point is inside the polygon
    #     intersection_point = self.camera.position + t * ray_direction

    #     u = np.dot(np.cross(v1 - v0, intersection_point - v0), normal)
    #     v = np.dot(np.cross(v2 - v1, intersection_point - v1), normal)
    #     w = np.dot(np.cross(v0 - v2, intersection_point - v2), normal)

    #     if all(0 <= val <= 1 for val in [u, v, w]):
    #         intersected_polygon = polygon_points
    #         return intersection_point, intersected_polygon

    #     return intersection_point, polygon_points

    def render(self):
        self.screen.fill((33, 50, 211))

        self.handle_input()
        rotate_h = rotate_matrix_y(self.camera.angle_h)
        rotate_v = rotate_matrix_x(self.camera.angle_v)

        sun = self.cubes[0]
        sun_center = sun.points[0]
        sun_center[0] += self.x
        sun_center = sun_center - self.camera.position
        sun_center = np.dot(sun_center, rotate_h)
        sun_center = np.dot(sun_center, rotate_v)

        self.draw_ground(rotate_h, rotate_v)

        sorted_cubes = get_sorted_cubes(self.cubes, self.camera.position)

        for cube in sorted_cubes:
            points = cube.points

            new_points = points - self.camera.position
            transformed_points = np.dot(new_points, rotate_h)
            transformed_points = np.dot(transformed_points, rotate_v)

            surfaces = get_surfaces(transformed_points)
            transformed_points = transform_points(
                transformed_points, self.camera.f)
            points_2d = np.dot(self.camera.K, transformed_points.T).T
            at_least_one_point_in_view = any(
                0 <= point[0] < screen_width and 0 <= point[1] < screen_height for point in points_2d
            )
            for surface in surfaces[3:]:
                # check if collid

                if at_least_one_point_in_view and all(
                    point[-1] > self.camera.f for _, point in surface
                ):
                    pts = [points_2d[point] for point, _ in surface]

                    surface_points = np.array([a for _, a in surface])

                    intensity = simulate_sunlight(surface_points, sun_center)

                    if cube == self.cubes[0]:
                        intensity = 1
                    draw_polygon(self.screen, pts, cube.texture, intensity)

        self.screen.blit(gui["crosshair"], (half_width -
                         gui["crosshair"].get_width()//2, half_height - gui["crosshair"].get_height()//2))

        self.screen.blit(gui["inventory"], self.inventory_bar_position)

        self.render_inventory_bar()

    def run(self):

        bg_idx = 1
        i = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = pygame.mouse.get_pos()

                    # if self.scene == Scenes.game:
                    #     forward_vector = np.array(
                    #         [
                    #             np.sin(self.camera.angle_h),
                    #             -np.sin(self.camera.angle_v),
                    #             np.cos(self.camera.angle_h),
                    #         ]
                    #     )
                    #     # dist = np.sqrt(
                    #     #     np.sum((self.camera.position[:2]-np.array([x, y]))**2))
                    #     new_cube_position = self.camera.position + 10 * forward_vector
                    #     if new_cube_position[1] > 1:
                    #         new_cube_position[1] = 1

                    #     new_cube = Cube(new_cube_position,
                    #                     2, textures8["sand"])
                    #     new_cube.texture = textures8[
                    #         list(textures8.keys())[self.selected_texture_index]
                    #     ]
                    #     self.sound.pick.play()
                    #     self.cubes.append(new_cube)

                    if self.scene == Scenes.game:
                        forward_vector = np.array([
                            np.sin(self.camera.angle_h),
                            -np.sin(self.camera.angle_v),
                            np.cos(self.camera.angle_h),
                        ])

                        intersection_cube = self.get_intersection_cube(
                            self.camera.position, forward_vector
                        )

                        if intersection_cube:
                            # Create a new cube above the pointed cube
                            new_cube_position = intersection_cube.center + \
                                np.array([0, -CUBE_SIZE, 0])
                            new_cube = Cube(new_cube_position,
                                            CUBE_SIZE, textures8["sand"])
                            new_cube.texture = textures8[
                                list(textures8.keys())[
                                    self.selected_texture_index]
                            ]
                            self.cubes.append(new_cube)

                        else:

                            intersection_point = self.get_ground_intersection(
                                forward_vector)
                            print(intersection_point)
                            if intersection_point is not None:
                                new_cube_position = intersection_point
                                new_cube_position[1] -= CUBE_SIZE//2

                                new_cube = Cube(new_cube_position,
                                                CUBE_SIZE, textures8["sand"])
                                new_cube.texture = textures8[list(textures8.keys())[
                                    self.selected_texture_index]]
                                self.sound.pick.play()
                                self.cubes.append(new_cube)

                    if self.scene == Scenes.menu:
                        if preview_button_rect.collidepoint((x, y)):
                            self.sound.menu.stop()
                            self.sound.click.play()
                            self.scene = Scenes.game
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                    self.selected_texture_index -= 1
                    if self.selected_texture_index < 0:
                        self.selected_texture_index = self.textures_per_row - 1
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                    self.selected_texture_index += 1
                    if self.selected_texture_index >= self.textures_per_row:
                        self.selected_texture_index = 0
            if self.scene == Scenes.loading:
                self.screen.fill((255, 255, 255))
                self.screen.blit(minecraft_logo, minecraft_logo_rect)

            if self.scene == Scenes.menu:
                self.sound.menu.play()
                pygame.mouse.set_visible(True)
                self.screen.blit(bgs[bg_idx], (0, 0))

                self.screen.blit(preview_button, preview_button_rect)
                self.screen.blit(join_button, join_button_rect)
                i += 1
                if i % 100 == 0:
                    bg_idx += 1
                if bg_idx > 5:
                    bg_idx = 1
            if self.scene == Scenes.game:

                pygame.mouse.set_visible(False)
                self.render()
            pygame.display.update()

            if self.scene == Scenes.loading:
                pygame.time.delay(1500)
                self.scene = Scenes.menu

            self.clock.tick(60)
