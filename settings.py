import numpy as np
import pygame
from cube import Cube

pygame.init()
info = pygame.display.Info()

# Get screen width and height
# screen_width = info.current_w
# screen_height = info.current_h
screen_width = 800
screen_height = 600

half_width = screen_width//2
half_height = screen_height//2


# SCREEN_W = 1080
# SCREEN_H = 700


BLACK = (0, 0, 0)

CUBE_SIZE = 2
CUBE_RAD = 2
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


textures16 = {
    "lava": pygame.image.load("assets\lava.png"),
    "grass": pygame.image.load("assets\grass t.png"),
    "bedrock": pygame.image.load(r"assets\bedrock.png"),
    "sand": pygame.image.load(r"assets\sand.png"),
    "brick": pygame.image.load(r"assets\brick.png"),
    "redwool": pygame.image.load(r"assets\red_wool.png"),
    "cobblestone": pygame.image.load("assets\cobblestone.png"),
    "grasstop": pygame.image.load(r"assets\grass s.png"),
    "tall_grass": pygame.image.load(r"assets\tall_grass.png"),
    "wood": pygame.image.load(r"assets\log_oak t.png"),
}
textures8 = {
    "lava": pygame.transform.scale(pygame.image.load("assets\lava.png"), (8, 8)),
    "grass": pygame.transform.scale(pygame.image.load("assets\grass t.png"), (8, 8)),
    "bedrock": pygame.transform.scale(pygame.image.load(r"assets\bedrock.png"), (8, 8)),
    "sand": pygame.transform.scale(pygame.image.load(r"assets\sand.png"), (8, 8)),
    "brick": pygame.transform.scale(pygame.image.load(r"assets\brick.png"), (8, 8)),
    "redwool": pygame.transform.scale(pygame.image.load(r"assets\red_wool.png"), (8, 8)),
    "cobblestone": pygame.transform.scale(pygame.image.load("assets\cobblestone.png"), (8, 8)),
    "water": pygame.transform.scale(pygame.image.load(r"assets\water.png"), (8, 8)),
    "tall_grass": pygame.transform.scale(pygame.image.load(r"assets\tall_grass.png"), (8, 8)),
    "wood": pygame.transform.scale(pygame.image.load(r"assets\log_oak t.png"), (8, 8)),
}
textures4 = {
    "lava": pygame.transform.scale(pygame.image.load("assets\lava.png"), (4, 4)),
    "grass": pygame.transform.scale(pygame.image.load("assets\grass t.png"), (4, 4)),
    "bedrock": pygame.transform.scale(pygame.image.load(r"assets\bedrock.png"), (4, 4)),
    "sand": pygame.transform.scale(pygame.image.load(r"assets\sand.png"), (4, 4)),
    "brick": pygame.transform.scale(pygame.image.load(r"assets\brick.png"), (4, 4)),
    "redwool": pygame.transform.scale(pygame.image.load(r"assets\red_wool.png"), (4, 4)),
    "cobblestone": pygame.transform.scale(pygame.image.load("assets\cobblestone.png"), (4, 4)),
    "grasstop": pygame.transform.scale(pygame.image.load(r"assets\grass s.png"), (4, 4)),
    "tall_grass": pygame.transform.scale(pygame.image.load(r"assets\tall_grass.png"), (4, 4)),
    "wood": pygame.transform.scale(pygame.image.load(r"assets\log_oak t.png"), (4, 4)),
}


class Scenes:
    loading = "loading"
    menu = "menu"
    game = "game"


minecraft_logo = pygame.image.load("gui\game_logo.png")
minecraft_logo_rect = minecraft_logo.get_rect(
    topleft=(half_width-minecraft_logo.get_width()//2, half_height-minecraft_logo.get_height()//2))


bgs = {
    1: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama0.png"), (screen_width, screen_height)),
    2: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama1.png"), (screen_width, screen_height)),
    3: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama2.png"), (screen_width, screen_height)),
    4: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama3.png"), (screen_width, screen_height)),
    5: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama4.png"), (screen_width, screen_height)),
    6: pygame.transform.smoothscale(pygame.image.load(r"gui\bg\panorama5.png"), (screen_width, screen_height))
}


font = pygame.font.Font("assets\main.ttf", 22)  # Default font with size 36

# Function to create a button


# def create_button(screen, rect, text, color):
#     pygame.draw.rect(screen, color, rect)
#     text_surface = font.render(text, True, (70, 30, 50))
#     text_rect = text_surface.get_rect(center=rect.center)
#     screen.blit(text_surface, text_rect)


def create_button(rect, text, color):
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    button_surface.fill(color)
    pygame.draw.rect(button_surface, color,
                     button_surface.get_rect(), border_radius=10)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=button_surface.get_rect().center)
    button_surface.blit(text_surface, text_rect)
    return button_surface


preview_button_rect = pygame.Rect(
    screen_width//2-80, screen_height//2-25, 160, 50)

preview_button = create_button(preview_button_rect,
                               "Preview", (0, 0, 0, 128))
join_button_rect = pygame.Rect(
    screen_width//2-125, screen_height//2+60, 250, 50)


join_button = create_button(join_button_rect,
                            "Join the server", (0, 0, 0, 128))


gui = {
    "inventory": pygame.transform.scale(pygame.image.load(r"assets\inventory.png"), (400, 50)),
    "crosshair": pygame.image.load(r"assets\crosshair.png"),
    "hover_slot": pygame.transform.scale(pygame.image.load(r"assets\hover_slot.png"), (50, 50)),
}


class Sound:
    pick = pygame.mixer.Sound(
        'sounds\pick.mp3')
    menu = pygame.mixer.Sound(
        'sounds\music\menu\menu4.ogg')
    dig = pygame.mixer.Sound(
        r'sounds\dig\grass3.ogg')
    click = pygame.mixer.Sound(
        'sounds\gui\click_stereo1.ogg')
    walk_name = "wood"
    walk = [
      
        pygame.mixer.Sound(
            f'sounds\step\{walk_name}1.ogg'),
        pygame.mixer.Sound(
            f'sounds\step\{walk_name}2.ogg'),
        pygame.mixer.Sound(
           f'sounds\step\{walk_name}3.ogg'),
        pygame.mixer.Sound(
            f'sounds\step\{walk_name}4.ogg'),
        pygame.mixer.Sound(
            f'sounds\step\{walk_name}5.ogg'),
        pygame.mixer.Sound(
            f'sounds\step\{walk_name}6.ogg'),
            ]


initial_cubes = [
    Cube((0, -150, -15), 0.3, textures8["sand"]),
    Cube((0, 2.5, 0), 0.5, textures8["lava"]),
    Cube((0, 2, 0), 0.5, textures8["lava"]),
    Cube((0, 1.5, 0), 0.5, textures8["lava"]),
    Cube((0, 1, 0), 0.5, textures8["lava"]),
    Cube((0, 0.5, 0), 0.5, textures8["lava"]),
    Cube((0, -0.75, 0.5), 2, textures8["grass"]),
    Cube((0, -0.75, -0.5), 2, textures8["grass"]),
]
