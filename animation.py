"""
Short example: animate frames from a tileset using tileset.py.
"""
import pygame
import sys

from tileset import Tileset

# Frame rects in tileset: (offset_x, offset_y, tile_w, tile_h)
FRAME_RECTS = [
   
    
    [
      24,
      71,
      272,
      385
    ]
    ,
    [
      1101,
      71,
      403,
      387
    ]
    ,
    [
      452,
      542,
      379,
      385
    ]
]


SCREEN_SIZE = (400, 400)
FRAME_DELAY_MS = 500
FPS = 60

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("Tileset animation")

# Load tileset and create animation source
tileset = Tileset("image_2026-02-12_18-00-04 (2).png", FRAME_RECTS)
if not tileset.is_loaded():
    print("Place image.png in this folder and run again.")
    sys.exit(1)

current_frame = 0
last_switch_time = pygame.time.get_ticks()
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    now = pygame.time.get_ticks()
    if now - last_switch_time >= FRAME_DELAY_MS:
        current_frame = (current_frame + 1) % tileset.num_frames()
        last_switch_time = now

    frame_image = tileset.get_frame(current_frame)
    screen.fill((255, 255, 255))
    if frame_image is not None:
        screen.blit(frame_image, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
