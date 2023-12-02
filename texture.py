import pygame
import numpy as np


def interpolate(p1, p2, f):
    return p1 + f * (p2 - p1)


def interpolate2d(p1, p2, f):
    return tuple(interpolate(p1[i], p2[i], f) for i in range(2))


def draw_polygon(surface, quad, img, intensity, hoverd=False):
    points = dict()

    for i in range(img.get_size()[1]+1):
        b = interpolate2d(quad[1], quad[2], i/img.get_size()[1])
        c = interpolate2d(quad[0], quad[3], i/img.get_size()[1])
        for u in range(img.get_size()[0]+1):
            a = interpolate2d(c, b, u/img.get_size()[0])
            points[(u, i)] = a

    for x in range(img.get_size()[0]):
        for y in range(img.get_size()[1]):
            color = tuple([int(i*intensity) for i in img.get_at((x, y))])
            if hoverd:
                pygame.draw.polygon(
                    surface,
                    get_hover_color(color),
                    [points[(x, y)], points[(x, y+1)],
                     points[(x+1, y+1)], points[(x+1, y)]]
                )

            else:
                pygame.draw.polygon(
                    surface,
                    color,
                    [points[(x, y)], points[(x, y+1)],
                     points[(x+1, y+1)], points[(x+1, y)]]
                )


def get_hover_color(base_color, hover_factor=2):

    base_color = tuple(int(max(0, min(255, channel)))
                       for channel in base_color)

    # Adjust the brightness for the hover effect
    hover_color = tuple(int(min(255, channel * hover_factor))
                        for channel in base_color)

    return hover_color
