"""
cut_tiles.py - Cut a tileset into a grid and save tile boxes (rects), not images.
Python 3.8 compatible.

Usage:
  python cut_tiles.py [image_path] [tile_w] [tile_h] [out_file]

Defaults: image.png, 32, 32, tiles_boxes.json
"""
import json
import os
import sys

import pygame


def cut_tileset_boxes(image_path, tile_width, tile_height, out_path="tiles_boxes.json"):
    """
    Load image, compute tile grid (tile_width x tile_height), save boxes as JSON.
    Box format: list of [x, y, w, h].
    Returns number of boxes, or -1 on error.
    """
    try:
        surface = pygame.image.load(image_path)
        surface = surface.convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        print("Error loading image: {}".format(e))
        return -1

    w, h = surface.get_size()
    cols = max(1, w // tile_width)
    rows = max(1, h // tile_height)

    boxes = []
    for row in range(rows):
        for col in range(cols):
            x = col * tile_width
            y = row * tile_height
            boxes.append([x, y, tile_width, tile_height])

    data = {
        "image": os.path.basename(image_path),
        "tile_width": tile_width,
        "tile_height": tile_height,
        "cols": cols,
        "rows": rows,
        "boxes": boxes,
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    return len(boxes)


def main():
    pygame.init()
    # Required so image load/convert_alpha works without "No video mode has been set"
    pygame.display.set_mode((1, 1))

    image_path = "image.png"
    tile_w = 32
    tile_h = 32
    out_path = "tiles_boxes.json"

    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
    if len(sys.argv) >= 3:
        tile_w = int(sys.argv[2])
    if len(sys.argv) >= 4:
        tile_h = int(sys.argv[3])
    if len(sys.argv) >= 5:
        out_path = sys.argv[4]

    if not os.path.isfile(image_path):
        print("File not found: {}".format(image_path))
        sys.exit(1)

    n = cut_tileset_boxes(image_path, tile_w, tile_h, out_path)
    if n >= 0:
        print("Saved {} boxes to {}".format(n, out_path))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
