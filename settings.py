import numpy as np
import pygame

SCREEN_W = 1080
SCREEN_H = 700


BLACK = (0, 0, 0)


MOVEMENT_SPEED = 0.5
ROTATION_SPEED = 0.1





colors_dic = {
    "0123": (255, 255, 255),
    "4567": (255, 0, 0),
    "0154": (0, 255, 0),
    "2376": (0, 0, 255),
    "1265": (255, 255, 0),
    "0374": (255, 0, 255)
}

colors = [(255, 255, 255),
          (255, 0, 0),
          (0, 255, 0),
          (0, 0, 255),
          (255, 255, 0),
          (255, 0, 255)]


textures = {
    "lava":pygame.transform.scale (pygame.image.load("assets\lava.png"),(16,16)),
    "grass": pygame.transform.scale (pygame.image.load("assets\grass t.png"),(16,16)),
    "bedrock":pygame.transform.scale ( pygame.image.load(r"assets\bedrock.png"),(4,4)),
    "sand": pygame.transform.scale ( pygame.image.load(r"assets\sand.png"),(4,4)),
    "brick": pygame.image.load(r"assets\brick.png"),
    "redwool": pygame.image.load(r"assets\red_wool.png"),
    "cobblestone": pygame.image.load("assets\cobblestone.png"),
    "grasstop": pygame.image.load(r"assets\grass s.png"),
}

gui = {
    "inventory": pygame.transform.scale(pygame.image.load(r"assets\inventory.png"),(400,50)),
    "crosshair": pygame.image.load(r"assets\crosshair.png"),
    "hover_slot": pygame.transform.scale(pygame.image.load(r"assets\hover_slot.png"),(50,50)),
}
