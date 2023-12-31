import math
import pygame
import sys
import numpy as np
from settings import *
from cube import *
from camera import *
from texture import *
from help import *
from network import Network
from player import Player


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
        self.angle_v_p = 0
        self.angle_h_p = 0
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.camera = Camera()
        self.clock = pygame.time.Clock()
        # cubes
        self.cubes = []
        self.con = ""
        # move
        self.i_walk = 0
        self.acceleration = 0
        self.x = 0
        self.sensitivity = 0.005
        self.sound = Sound()
        # mouse
        self.mouse_button_state = pygame.mouse.get_pressed()
        self.mouse_button_timer = 0
        self.mouse_button_delay = 100
        self.mouse_button_down = False
        # ground
        self.ground = generate_ground()

        self.ground_under_player = -2
        # tools
        self.scene = Scenes.loading
        self.add_cubes_sound = None

        self.mouse_button_down = False
        self.hovered_polygon = None
        self.hovered_face = None
        self.sorted_cubes = None
        self.hoverd_cube = None
        self.sun = Cube((78, -150, -15), 0.3, Texture.sand)
        self.other_players = []
        self.other_players_rotation_h = None
        self.other_players_rotation_v = None

    def handle_input(self):

        mouse_state = pygame.mouse.get_pressed()
        clicked = [p - s for p, s in zip(mouse_state, self.mouse_button_state)]

        self.mouse_button_state = mouse_state

        if clicked[0] == 1:  # Left mouse button pressed
            self.mouse_button_down = True
            self.mouse_button_timer = pygame.time.get_ticks()
            pygame.time.set_timer(pygame.USEREVENT, self.mouse_button_delay)

        if clicked[0] == -1:  # Left mouse button released
            pygame.time.set_timer(pygame.USEREVENT, 0)  # Stop the timer
            self.mouse_button_down = False

        if self.mouse_button_down:

            forward_vector = np.array([
                np.sin(self.camera.angle_h) * np.cos(self.camera.angle_v),
                -np.sin(self.camera.angle_v),
                np.cos(self.camera.angle_h) * np.cos(self.camera.angle_v),
            ])

            intersection_cube, intersection_pt = self.get_intersection_cube(
                self.camera.position, forward_vector
            )

            if intersection_cube:
                closest_face_index = intersection_cube.get_intersected_face_index(
                    intersection_pt, intersection_cube)
                face_vertex_indices = [
                    # y
                    [0, 1, 5, 4],
                    [2, 3, 7, 6],

                    # z
                    [1, 0, 3, 2],
                    [4, 5, 6, 7],
                    # x
                    [1, 2, 6, 5],
                    [3, 0, 4, 7]
                ]

                self.hovered_face = face_vertex_indices[closest_face_index]
                self.hoverd_cube = intersection_cube
                self.hovered_polygon = None
            else:
                intersection_point, intersected_polygon = self.get_ground_intersection(
                    forward_vector)
                # Store the intersected polygon for hover effect
                self.hovered_polygon = intersected_polygon
                self.hovered_face = []

            self.mouse_button_down = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # use space to jump
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.acceleration = -0.2
                    self.camera.position[1] += self.acceleration
                    # self.sound.jump.play()
        mouse_rel = pygame.mouse.get_rel()
        pygame.mouse.set_pos(half_width, half_height)
        self.camera.angle_h += self.sensitivity * mouse_rel[0]
        self.camera.angle_v += self.sensitivity * (-mouse_rel[1])
        self.angle_h_p -= self.sensitivity * mouse_rel[0]
        self.angle_v_p -= self.sensitivity * (-mouse_rel[1])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

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
            new_position = self.camera.position.copy()
            new_position[2] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            new_position[0] -= MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            if not self.check_collision(new_position):
                self.camera.position = new_position

        if keys[pygame.K_d]:
            new_position = self.camera.position.copy()
            new_position[2] -= MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            new_position[0] += MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            if not self.check_collision(new_position):
                self.camera.position = new_position

        if keys[pygame.K_w]:
            new_position = self.camera.position.copy()
            new_position[2] += MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            new_position[0] += MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            if not self.check_collision(new_position):
                self.camera.position = new_position
            self.sound.walk[self.i_walk % len(self.sound.walk)].set_volume(.1)
            self.sound.walk[self.i_walk % len(self.sound.walk)].play()
            self.i_walk += 1

        if keys[pygame.K_s]:
            new_position = self.camera.position.copy()
            new_position[2] -= MOVEMENT_SPEED * np.cos(self.camera.angle_h)
            new_position[0] -= MOVEMENT_SPEED * np.sin(self.camera.angle_h)
            if not self.check_collision(new_position):
                self.camera.position = new_position
        if keys[pygame.K_r]:
            self.cubes = initial_cubes

        if keys[pygame.K_LEFT]:
            self.selected_texture_index -= 1
            pygame.time.delay(100)
        if keys[pygame.K_RIGHT]:
            self.selected_texture_index += 1
            pygame.time.delay(100)

        if keys[pygame.K_q]:
            new_position = self.camera.position.copy()
            new_position[1] -= 2
            if not self.check_collision(new_position):
                self.camera.position = new_position
        if keys[pygame.K_e]:
            new_position = self.camera.position.copy()
            new_position[1] += 1
            if not self.check_collision(new_position):
                self.camera.position = new_position

        if self.camera.position[1] < -2:
            self.acceleration += 0.1

            if not self.check_collision(self.camera.position+np.array([0, self.acceleration, 0])):

                self.camera.position[1] = self.camera.position[1] + \
                    self.acceleration
            else:
                self.acceleration = 0.2

        else:
            # self.camera.position[1] = -3
            self.acceleration = 0.2

    def check_collision(self, new_position):
        player_point = np.array(
            [new_position[0], new_position[1], new_position[2]])

        player_width = 0
        player_height = 1.5

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

                return True

        return False

    def draw_ground(self, rotate_h, rotate_v):

        for i, polygon in enumerate(self.ground):
            length = len(self.ground)
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

                base_color = (np.round(i*255 / length),
                              np.round(i * 255 / length), 5)
                hover_color = tuple(min(c + 50, 255) for c in base_color)
                if np.array_equal(polygon, self.hovered_polygon) and self.mouse_button_down:
                    pygame.draw.polygon(
                        self.screen, hover_color, points_2d)
                else:
                    pygame.draw.polygon(
                        self.screen, base_color, points_2d)
                # draw_polygon(self.screen, points_2d, pygame.image.load(
                #     r"assets\bedrock.png"), 1)

    def get_ground_intersection(self, ray_direction):

        polygon = self.ground[1]

        if self.is_ray_intersects_polygon(ray_direction, polygon):

            normal = np.cross(polygon[1] - polygon[0],
                              polygon[2] - polygon[0])

            intersection_point = ray_plane_intersection(
                self.camera.position, ray_direction,
                normal,
                polygon[0]
            )

            for polygon in self.ground:
                if point_in_polygon(intersection_point, polygon):

                    return intersection_point, polygon

        return None, None

    def is_ray_intersects_polygon(self, ray_direction, polygon_points):

        v0, v1, v2, _ = polygon_points

        # Calculate the normal of the polygon
        normal = np.cross(v1 - v0, v2 - v0)

        # Check if the ray is parallel to the plane of the polygon
        dot_product = np.dot(normal, ray_direction)

        if dot_product > -1e-6:
            return False

        return True

    def get_intersection_cube(self, origin, direction):

        for cube in reversed(self.sorted_cubes):
            intersection_point = cube.ray_intersection(origin, direction)
            if intersection_point is not None:
                return cube, intersection_point
        return None, None

    def render_inventory_bar(self):

        current_x, current_y = self.inventory_bar_position
        y = current_y + 10
        x = current_x + 10
        for i in range(self.textures_per_row):

            texture_image = pygame.transform.scale(
                list(textures16.values())[i], (30, 30))
            self.screen.blit(texture_image, (x, y))

            if i == self.selected_texture_index:
                self.screen.blit(gui["hover_slot"], (current_x, current_y))

            x += self.texture_slot_size - 1
            current_x += self.texture_slot_size - 1

            # Move to the next row after reaching the maximum number of textures per row
            # if (i + 1) % self.textures_per_row == 0:
            #     current_x = self.inventory_bar_position[0]
            #     current_y += self.texture_slot_size

    def rotate_other_player_cube(self, points, angle_h, angle_v):

        rotate_h = rotate_matrix_y(angle_h)
        rotate_v = rotate_matrix_x(angle_v)

        rotated_points = np.dot(points - self.other_players.center, rotate_h)
        rotated_points = np.dot(rotated_points, rotate_v)

        return rotated_points

    def render(self):
        self.screen.fill((33, 50, 211))

        self.handle_input()
        rotate_h = rotate_matrix_y(self.camera.angle_h)
        rotate_v = rotate_matrix_x(self.camera.angle_v)

        sun_center = self.sun.points[0]
        sun_center[0] += self.x
        sun_center = sun_center - self.camera.position
        sun_center = np.dot(sun_center, rotate_h)
        sun_center = np.dot(sun_center, rotate_v)
        self.draw_ground(rotate_h, rotate_v)

        body_cubes = []
        players_cubes = []
        for pl in self.other_players:
            head_position = pl[0].center
            players_cubes.append(pl[0])

            # Body
            body_cubes.append(Cube(
                [head_position[0], head_position[1] + 0.7, head_position[2]], 0.7, "bedrock"))
            body_cubes.append(Cube(
                [head_position[0], head_position[1] + 1.4, head_position[2]], 0.7, "bedrock"))
            body_cubes.append(Cube(
                [head_position[0], head_position[1] + 2.1, head_position[2]], 0.7, "bedrock"))

            body_cubes.append(Cube(
                [head_position[0]+0.3, head_position[1] + 0.5, head_position[2]], 0.4, "bedrock"))
            body_cubes.append(Cube(
                [head_position[0]-0.3, head_position[1] + 0.5, head_position[2]], 0.4, "bedrock"))

        drawing_cubes = self.cubes+players_cubes+body_cubes

        self.sorted_cubes = get_sorted_cubes(
            drawing_cubes, self.camera.position)

        for cube in self.sorted_cubes:
            if cube in players_cubes:
                idx = players_cubes.index(cube)
                _, r_h, r_v = self.other_players[idx]
                rotation_matri_x = np.array([
                    [1, 0, 0],
                    [0, np.cos(r_v), -
                     np.sin(r_v)],
                    [0, np.sin(r_v),
                     np.cos(r_v)]
                ])

                rotation_matri_y = np.array([
                    [np.cos(r_h), 0,
                     np.sin(r_h)],
                    [0, 1, 0],
                    [-np.sin(r_h), 0,
                     np.cos(r_h)]
                ])

                rotated_vertices = np.dot(np.dot(cube.points-cube.center,
                                          rotation_matri_x), rotation_matri_y)+cube.center

                new_points = rotated_vertices - self.camera.position

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

                    if at_least_one_point_in_view and all(
                        point[-1] > self.camera.f for _,  point in surface[1]
                    ):
                        pts = []
                        # lwjah = surface[0]
                        for point, _ in surface[1]:
                            pts.append(points_2d[point])

                        ptsd = [point for point, _ in surface[1]]

                        surface_points = np.array([a for _, a in surface[1]])

                        intensity = simulate_sunlight(
                            surface_points, sun_center)
                        if surface[0] == "front":
                            draw_polygon(self.screen, pts,
                                         face_texture, intensity)
                        else:
                            draw_polygon(self.screen, pts,
                                         side_face_texture, 0)
            else:

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

                    if at_least_one_point_in_view and all(
                        point[-1] > self.camera.f for _,  point in surface[1]
                    ):
                        pts = []
                        # lwjah = surface[0]
                        for point, _ in surface[1]:
                            pts.append(points_2d[point])

                        ptsd = [point for point, _ in surface[1]]

                        surface_points = np.array([a for _, a in surface[1]])

                        intensity = simulate_sunlight(
                            surface_points, sun_center)
                        if cube in body_cubes:

                            draw_polygon(self.screen, pts,
                                         body, intensity)

                        else:
                            if self.hoverd_cube != None:
                                if np.array_equal(cube.center, self.hoverd_cube.center):
                                    if np.array_equal(np.sort(ptsd), np.sort(self.hovered_face)):

                                        draw_polygon(self.screen, pts,
                                                     textures8[cube.texture], 1, True)
                                        self.hovered_face = []
                                    else:

                                        draw_polygon(self.screen, pts,
                                                     textures8[cube.texture], intensity)
                                else:
                                    draw_polygon(self.screen, pts,
                                                 textures8[cube.texture], intensity)

                            else:

                                draw_polygon(self.screen, pts,
                                             textures8[cube.texture], intensity)

        self.other_players = []
        self.screen.blit(gui["crosshair"], (half_width -
                         gui["crosshair"].get_width()//2, half_height - gui["crosshair"].get_height()//2))

        self.screen.blit(gui["inventory"], self.inventory_bar_position)

        self.render_inventory_bar()

    def run(self):

        bg_idx = 1
        i = 0
        n = Network()
        p_id = n.game_info["p_id"]
        players = n.game_info["players"]
        cubes = n.game_info["cubes"]
        self.cubes = cubes
        self.camera.position = players[p_id].position
        self.player = Player(
            players[p_id], players[p_id].rotation_h, players[p_id].rotation_v)

        while True:

            players[p_id].position = self.camera.position
            players[p_id].rotation_v = self.angle_v_p
            players[p_id].rotation_h = self.angle_h_p

            data = n.send(
                {"p_id": p_id, "players": players,
                    "cubes": self.cubes, "con": self.con}
            )

            players = data["players"]
            if len(players) > 1:

                for id, player in enumerate(players):
                    if p_id != id:
                        self.other_players.append(
                            (Cube(player.position, .4, "bedrock"), player.rotation_h, player.rotation_v))

            cubes = data["cubes"]
            self.cubes = cubes
            self.con = data["con"]
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.con = "add"
                    x, y = pygame.mouse.get_pos()

                    if self.scene == Scenes.game:

                        forward_vector = np.array([
                            np.sin(self.camera.angle_h) *
                            np.cos(self.camera.angle_v),
                            -np.sin(self.camera.angle_v),
                            np.cos(self.camera.angle_h) *
                            np.cos(self.camera.angle_v),
                        ])

                        intersection_cube, intersection_pt = self.get_intersection_cube(
                            self.camera.position, forward_vector
                        )

                        if intersection_cube:
                            closest_face_index = intersection_cube.get_intersected_face_index(
                                intersection_pt, intersection_cube)

                            # Define offsets for each face
                            face_offsets = [
                                np.array([0, -CUBE_SIZE, 0]),   # Top face
                                np.array([0, CUBE_SIZE, 0]),  # Bottom face
                                np.array([0, 0, -CUBE_SIZE]),   # Front face
                                np.array([0, 0, CUBE_SIZE]),  # Back face
                                np.array([CUBE_SIZE, 0, 0]),   # left face
                                np.array([-CUBE_SIZE, 0, 0]),  # right face
                            ]

                            # Use the offset corresponding to the closest face to place the new cube
                            new_cube_position = intersection_cube.center + \
                                face_offsets[closest_face_index]
                            # Create a new cube only if the cube will not colide with me

                            if (math.dist(new_cube_position, self.camera.position) > CUBE_SIZE + 3
                                and not any(
                                    np.array_equal(new_cube_position, c.center)
                                    for c in self.cubes
                            )
                                and new_cube_position[1] < 2
                            ):
                                new_cube = Cube(new_cube_position,
                                                CUBE_SIZE, Texture.sand)
                                new_cube.texture = list(textures8.keys())[
                                    self.selected_texture_index]
                                # if self.selected_texture_index==0:
                                #     new_cube.texture

                                # Texture.
                                self.sound.pick.play()
                                self.cubes.append(new_cube)
                                self.mouse_button_down = False
                                self.hovered_polygon = None

                        else:

                            intersection_point, intersection_polygon = self.get_ground_intersection(
                                forward_vector)
                            # set the position of the new polygon above the intersection polygon
                            if intersection_polygon is not None:
                                new_cube_position = np.mean(
                                    intersection_polygon, axis=0)+np.array([0, -CUBE_SIZE//2, 0])

                                new_cube = Cube(new_cube_position,
                                                CUBE_SIZE, Texture.sand)
                                new_cube.texture = list(textures8.keys())[
                                    self.selected_texture_index]
                                self.sound.pick.play()

                                self.cubes.append(new_cube)

                            elif intersection_point is not None:
                                new_cube_position = intersection_point[0]
                                new_cube_position[1] -= CUBE_SIZE//2

                                new_cube = Cube(new_cube_position,
                                                CUBE_SIZE, Texture.sand)
                                new_cube.texture = list(textures8.keys())[
                                    self.selected_texture_index]
                                self.sound.pick.play()
                                self.cubes.append(new_cube)

                    if self.scene == Scenes.menu:
                        if join_button_rect.collidepoint((x, y)):
                            self.sound.menu.stop()
                            self.sound.click.play()
                            self.scene = Scenes.game
                # remove a cube using mouse button 3
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    self.con = "remove"
                    x, y = pygame.mouse.get_pos()
                    if self.scene == Scenes.game:
                        forward_vector = np.array([
                            np.sin(self.camera.angle_h) *
                            np.cos(self.camera.angle_v),
                            -np.sin(self.camera.angle_v),
                            np.cos(self.camera.angle_h) *
                            np.cos(self.camera.angle_v),
                        ])

                        intersection_cube, _ = self.get_intersection_cube(
                            self.camera.position, forward_vector
                        )

                        if intersection_cube:
                            for c in self.cubes:
                                if np.array_equal(intersection_cube.center, c.center):
                                    self.cubes.remove(c)
                            # self.cubes.remove(intersection_cube)
                            self.sound.dig.set_volume(.5)
                            self.sound.dig.play()

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

            display_fps(self.screen, self.clock)
            pygame.display.update()

            if self.scene == Scenes.loading:
                pygame.time.delay(1500)
                self.scene = Scenes.menu

            self.clock.tick(60)
