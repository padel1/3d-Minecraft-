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
        self.inventory_bar_position = (200, 500)
        self.texture_slot_size = 45
        self.textures_per_row = 6
        self.selected_texture_index = 0
        #
        self.screen = pygame.display.set_mode((800, 600))
        self.camera = Camera()
        self.clock = pygame.time.Clock()
        # cubes
        self.cubes = [
            Cube((0, -150, -15), 0.3, textures["sand"]),
            Cube((0, 2.5, 0), 0.5, textures["lava"]),
            Cube((0, 2, 0), 0.5, textures["lava"]),
            Cube((0, 1.5, 0), 0.5, textures["lava"]),
            Cube((0, 1, 0), 0.5, textures["lava"]),
            Cube((0, 0.5, 0), 0.5, textures["lava"]),
            Cube((0, -0.75, 0.5), 2, textures["grass"]),
            Cube((0, -0.75, -0.5), 2, textures["grass"]),
        ]
        # move
        self.acceleration = 0
        self.x = 0
        self.sensitivity = 0.01
        pygame.mouse.set_visible(False)
        # ground
        self.ground = generate_ground()
        self.ground_under_player = -2

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                forward_vector = np.array(
                    [
                        np.sin(self.camera.angle_h),
                        -np.sin(self.camera.angle_v),
                        np.cos(self.camera.angle_h),
                    ]
                )
                new_cube_position = self.camera.position + 10 * forward_vector

                new_cube = Cube(new_cube_position, 3, textures["sand"])
                new_cube.texture = textures[
                    list(textures.keys())[self.selected_texture_index]
                ]
                self.cubes.append(new_cube)
        is_inside_cube = any(
            cube.center[1] / 2 - cube.size
            < self.camera.position[1] + 5
            < cube.center[1] / 2 + cube.size
            and cube.center[0] / 2 - cube.size
            < self.camera.position[0]
            < cube.center[0] / 2 + cube.size
            and cube.center[2] / 2 - cube.size
            < self.camera.position[2]
            < cube.center[2] / 2 + cube.size
            for cube in self.cubes
        )
        if is_inside_cube:
            self.camera.position[1] = -8
            self.ground_under_player = self.camera.position[1]
        else:
            self.ground_under_player = -2
        mouse_rel = pygame.mouse.get_rel()
        pygame.mouse.set_pos(400, 300)
        self.camera.angle_h += self.sensitivity * mouse_rel[0]
        self.camera.angle_v += self.sensitivity * (-mouse_rel[1])
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_SPACE]:
            pass
        if keys[pygame.K_6]:
            self.selected_texture_index = 0
        elif keys[pygame.K_7]:
            self.selected_texture_index = 1
        elif keys[pygame.K_8]:
            self.selected_texture_index = 2
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
        if keys[pygame.K_a]:
            self.camera.position[2] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            self.camera.position[0] -= MOVEMENT_SPEED * np.cos(self.camera.angle_h)
        if keys[pygame.K_d]:
            self.camera.position[2] -= MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            self.camera.position[0] += MOVEMENT_SPEED * np.cos(self.camera.angle_h)
        if keys[pygame.K_w]:
            self.camera.position[2] += MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            self.camera.position[0] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)
        if keys[pygame.K_s]:
            self.camera.position[2] -= MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            self.camera.position[0] -= MOVEMENT_SPEED * np.sin(self.camera.angle_h)
        if keys[pygame.K_n]:
            forward_vector = np.array(
                [np.sin(self.camera.angle_h), 0, np.cos(self.camera.angle_h)]
            )
            new_cube_position = self.camera.position + 10 * forward_vector
            new_cube_position[1] += 2

            new_cube = Cube(new_cube_position, 1.5, textures["sand"])
            self.cubes.append(new_cube)

        if keys[pygame.K_r]:
            self.cubes = [
                Cube((0, -150, -15), 0.3, textures["sand"]),
                Cube((0, 2.5, 0), 0.5, textures["lava"]),
                Cube((0, 2, 0), 0.5, textures["lava"]),
                Cube((0, 1.5, 0), 0.5, textures["lava"]),
                Cube((0, 1, 0), 0.5, textures["lava"]),
                Cube((0, 0.5, 0), 0.5, textures["lava"]),
                Cube((0, -0.75, 0.5), 2, textures["grass"]),
                Cube((0, -0.75, -0.5), 2, textures["grass"]),
            ]

        if keys[pygame.K_q]:
            self.camera.position[1] -= 2
        if keys[pygame.K_e]:
            self.camera.position[1] += MOVEMENT_SPEED
        if keys[pygame.K_LEFT]:
            self.camera.angle_h -= ROTATION_SPEED
        if keys[pygame.K_RIGHT]:
            self.camera.angle_h += ROTATION_SPEED
        if keys[pygame.K_UP]:
            self.camera.angle_v += ROTATION_SPEED
        if keys[pygame.K_DOWN]:
            self.camera.angle_v -= ROTATION_SPEED

        if self.camera.position[1] < self.ground_under_player:
            self.acceleration += 0.09
            self.camera.position[1] += self.acceleration
        else:
            self.acceleration = 0

    def draw_ground(self, rotate_h, rotate_v):
        for i, polygon in enumerate(self.ground):
            new_points = polygon - self.camera.position
            transformed_points = np.dot(new_points, rotate_h)
            transformed_points = np.dot(transformed_points, rotate_v)
            tra = transformed_points
            transformed_points = transform_points(transformed_points, self.camera.f)
            points_2d = np.dot(self.camera.K, transformed_points.T).T
            at_least_one_point_in_view = any(
                0 <= point[0] < 800 and 200 <= point[1] < 600 for point in points_2d
            )

            if at_least_one_point_in_view and all(
                point[-1] > self.camera.f for point in tra
            ):
                pygame.draw.polygon(self.screen, (32, np.round(i / 2), 5), points_2d)
                # draw_polygon(self.screen, points_2d, pygame.image.load(
                #     r"assets\bedrock.png"), 1)

    def render_inventory_bar(self):
        current_x, current_y = self.inventory_bar_position
        y = current_y + 10
        x = current_x + 9
        for i, texture_name in enumerate(textures.keys()):
            texture_image = pygame.transform.scale(textures[texture_name], (30, 30))
            self.screen.blit(texture_image, (x, y))

            if i == self.selected_texture_index:
                self.screen.blit(gui["hover_slot"], (current_x, current_y))

            x += self.texture_slot_size - 1
            current_x += self.texture_slot_size - 1

            # Move to the next row after reaching the maximum number of textures per row
            if (i + 1) % self.textures_per_row == 0:
                current_x = self.inventory_bar_position[0]
                current_y += self.texture_slot_size

    def render(self):
        self.screen.fill((0, 0, 0))

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
            transformed_points = transform_points(transformed_points, self.camera.f)
            points_2d = np.dot(self.camera.K, transformed_points.T).T
            at_least_one_point_in_view = any(
                0 <= point[0] < 800 and 0 <= point[1] < 600 for point in points_2d
            )
            for surface in surfaces[3:]:
                if at_least_one_point_in_view and all(
                    point[-1] > self.camera.f for _, point in surface
                ):
                    pts = [points_2d[point] for point, _ in surface]

                    surface_points = np.array([a for _, a in surface])

                    intensity = simulate_sunlight(surface_points, sun_center)

                    if cube == self.cubes[0]:
                        intensity = 1
                    draw_polygon(self.screen, pts, cube.texture, intensity)

        # draw the crosshair
        self.screen.blit(gui["crosshair"], (375, 285))
        # blitting the inventory
        self.screen.blit(gui["inventory"], self.inventory_bar_position)
        # blitting the selected texture
        self.render_inventory_bar()
        fps = int(self.clock.get_fps())
        pygame.display.set_caption(f"FPS: {fps}")
        pygame.display.update()
        self.clock.tick(60)

    def run(self):
        while True:
            self.render()
