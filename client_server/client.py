# client.py
import pygame
import socket
import pickle
import numpy as np
from help import *

class Client:
    def __init__(self, host, port):
        self.server_address = (host, port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.a=1

    def send_data(self, data):
        serialized_data = pickle.dumps(data)
        self.client_socket.send(serialized_data)

    def receive_data(self):
        data = self.client_socket.recv(1024)
        return pickle.loads(data)
    
    def draw_ground(self, rotate_h, rotate_v,ground,camera_position):
        for i, polygon in enumerate(self.ground):
            length = len(ground)
            new_points = polygon - camera_position
            transformed_points = np.dot(new_points, rotate_h)
            transformed_points = np.dot(transformed_points, rotate_v)
            tra = transformed_points
            transformed_points = transform_points(transformed_points, self.camera.f)
            points_2d = np.dot(self.camera.K, transformed_points.T).T
            at_least_one_point_in_view = any(
                0 <= point[0] < screen_width and 0 <= point[1] < screen_height
                for point in points_2d
            )

            if at_least_one_point_in_view and all(
                point[-1] > self.camera.f for point in tra
            ):
                base_color = (np.round(i * 255 / length), np.round(i * 255 / length), 5)
                hover_color = tuple(min(c + 50, 255) for c in base_color)
                if (
                    np.array_equal(polygon, self.hovered_polygon) and self.a==0
                    and self.mouse_button_down
                ):
                    pygame.draw.polygon(self.screen, hover_color, points_2d)
                else:
                    pygame.draw.polygon(self.screen, base_color, points_2d)
                # draw_polygon(self.screen, points_2d, pygame.image.load(
                #     r"assets\bedrock.png"), 1)


    def run(self):
        pygame.init()
        # Initialize your game components here
        # ...

        while True:
            # Handle user input, update game state, render, etc.
            # ...

            data_to_send = {}  # Put your game state data here
            self.send_data(data_to_send)

            received_data = self.receive_data()
            # Update your game state based on the received data
            # ...

if __name__ == "__main__":
    client = Client('localhost', 55555)
    client.run()
