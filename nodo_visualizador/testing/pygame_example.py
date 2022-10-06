#!/usr/bin/env python3

import pygame

# pygame render window
pygame.init()

output_w = 1280
output_h = 720
size = (output_w, output_h)
run = True

display = pygame.display.set_mode(size)
visualization = pygame.Surface(size, pygame.SRCALPHA)
pygame.display.set_caption("PYGAME EXAMPLE")


def draw_visualization():

    display.fill((0, 0, 0))

    # background
    color = (0, 0, 0, 3)
    pygame.draw.rect(visualization, color, pygame.Rect(0, 0, output_w, output_h))

    # draw a circle
    color = (255, 255, 255, 255)
    pygame.draw.circle(visualization, color, (int(output_w/2), int(output_h/2)), 100)

    display.blit(visualization, (0, 0))

    pygame.display.update()


while run:

    # 25 FPS
    pygame.time.delay(40)

    for event in pygame.event.get():
        # alt F4
        if event.type == pygame.QUIT:
            run = False

    draw_visualization()


pygame.quit()
