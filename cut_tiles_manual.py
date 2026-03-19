"""
cut_tiles_manual.py - Manually draw boxes on a tileset and save them.
Python 3.8 compatible.

Usage:
  python cut_tiles_manual.py [image_path] [out_file]

Controls:
  Mouse drag  - draw a box
  Backspace   - remove last box
  S           - save boxes and quit
  Q / Escape  - quit (without saving)
"""
import json
import os
import sys

import pygame


def get_display_rect(img_w, img_h, win_w, win_h):
    """Scale image to fit window, centered. Return (scaled_surface, offset_x, offset_y, scale)."""
    scale_w = win_w / img_w if img_w else 1
    scale_h = win_h / img_h if img_h else 1
    scale = min(scale_w, scale_h, 1.0)  # don't scale up
    sw, sh = int(img_w * scale), int(img_h * scale)
    off_x = (win_w - sw) // 2
    off_y = (win_h - sh) // 2
    return sw, sh, off_x, off_y, scale


def screen_to_image(sx, sy, off_x, off_y, scale):
    """Convert screen coords to image coords."""
    if scale <= 0:
        return 0, 0
    ix = int((sx - off_x) / scale)
    iy = int((sy - off_y) / scale)
    return ix, iy


def run_manual_cutter(image_path, out_path="tiles_manual.json"):
    pygame.init()
    win_w, win_h = 1024, 768
    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Manual tile cutter - drag to add box, Backspace remove last, S save, Q quit")

    try:
        surface = pygame.image.load(image_path)
        surface = surface.convert_alpha()
    except (pygame.error, FileNotFoundError) as e:
        print("Error loading image: {}".format(e))
        return False

    img_w, img_h = surface.get_size()

    boxes = []  # list of [x, y, w, h] in image coords
    drag_start = None  # (sx, sy) or None
    clock = pygame.time.Clock()

    while True:
        sw, sh, off_x, off_y, scale = get_display_rect(img_w, img_h, win_w, win_h)
        scaled = pygame.transform.scale(surface, (sw, sh)) if scale != 1.0 else surface

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.VIDEORESIZE:
                win_w, win_h = event.w, event.h
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and drag_start is None:
                    drag_start = event.pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drag_start is not None:
                    x1, y1 = screen_to_image(drag_start[0], drag_start[1], off_x, off_y, scale)
                    x2, y2 = screen_to_image(event.pos[0], event.pos[1], off_x, off_y, scale)
                    x = min(x1, x2)
                    y = min(y1, y2)
                    w = max(1, abs(x2 - x1))
                    h = max(1, abs(y2 - y1))
                    # Clamp to image
                    x = max(0, min(x, img_w - 1))
                    y = max(0, min(y, img_h - 1))
                    w = min(w, img_w - x)
                    h = min(h, img_h - y)
                    if w > 0 and h > 0:
                        boxes.append([x, y, w, h])
                    drag_start = None

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    return False
                if event.key == pygame.K_s:
                    data = {
                        "image": os.path.basename(image_path),
                        "boxes": boxes,
                    }
                    with open(out_path, "w") as f:
                        json.dump(data, f, indent=2)
                    print("Saved {} boxes to {}".format(len(boxes), out_path))
                    pygame.quit()
                    return True
                if event.key == pygame.K_BACKSPACE and boxes:
                    boxes.pop()

        screen.fill((40, 40, 40))
        screen.blit(scaled, (off_x, off_y))

        # Draw boxes (in screen coords)
        for (ix, iy, iw, ih) in boxes:
            sx = off_x + int(ix * scale)
            sy = off_y + int(iy * scale)
            sw_ = max(1, int(iw * scale))
            sh_ = max(1, int(ih * scale))
            pygame.draw.rect(screen, (0, 255, 0), (sx, sy, sw_, sh_), 2)

        # Draw current drag
        if drag_start is not None:
            mx, my = pygame.mouse.get_pos()
            x1, y1 = drag_start[0], drag_start[1]
            rx = min(x1, mx)
            ry = min(y1, my)
            rw = abs(mx - x1)
            rh = abs(my - y1)
            pygame.draw.rect(screen, (255, 255, 0), (rx, ry, rw, rh), 2)

        # Hint
        font = pygame.font.Font(None, 24)
        text = font.render("Drag: add box | Backspace: undo | S: save | Q: quit  [ {} boxes ]".format(len(boxes)), True, (200, 200, 200))
        screen.blit(text, (8, win_h - 24))

        pygame.display.flip()
        clock.tick(60)


def main():
    image_path = "image_2026-02-12_18-00-04 (2).png"
    out_path = "tiles_manual.json"
    if len(sys.argv) >= 2:
        image_path = sys.argv[1]
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]

    if not os.path.isfile(image_path):
        print("File not found: {}".format(image_path))
        sys.exit(1)

    run_manual_cutter(image_path, out_path)
    sys.exit(0)


if __name__ == "__main__":
    main()
