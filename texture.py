import pygame
import numpy as np


def interpolate(p1, p2, f):
    return p1 + f * (p2 - p1)


def interpolate2d(p1, p2, f):
    return tuple(interpolate(p1[i], p2[i], f) for i in range(2))




def draw_polygon(surface, quad, img, intensity):
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
            pygame.draw.polygon(
                surface,
                color,
                [points[(x, y)], points[(x, y+1)],
                 points[(x+1, y+1)], points[(x+1, y)]]
            )



