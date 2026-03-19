"""
tileset.py - Load a tileset image and extract frames by rects.
Python 3.8 compatible.
"""
import pygame


def load_tileset(path, use_alpha=True):
    """
    Load a tileset image from path.
    use_alpha: if True, use convert_alpha() for transparency.
    Returns a Surface or None on error.
    """
    try:
        surface = pygame.image.load(path)
        if use_alpha:
            return surface.convert_alpha()
        return surface.convert()
    except (pygame.error, FileNotFoundError):
        return None


def get_frame(tileset_surface, rect):
    """
    Get a subsurface (one tile/frame) from the tileset.
    rect: (x, y, width, height) or pygame.Rect.
    Returns Surface or None.
    """
    if tileset_surface is None:
        return None
    if not isinstance(rect, pygame.Rect):
        rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
    try:
        return tileset_surface.subsurface(rect)
    except ValueError:
        return None


class Tileset:
    """
    Holds a loaded tileset image and a list of frame rects.
    """

    def __init__(self, image_path, frame_rects, use_alpha=True):
        """
        image_path: path to tileset image.
        frame_rects: list of (x, y, w, h) or pygame.Rect for each frame.
        """
        self.surface = load_tileset(image_path, use_alpha=use_alpha)
        self.frame_rects = []
        for r in frame_rects:
            if isinstance(r, pygame.Rect):
                self.frame_rects.append(r)
            else:
                self.frame_rects.append(
                    pygame.Rect(r[0], r[1], r[2], r[3])
                )

    def get_frame(self, index):
        """Get frame Surface by index (0-based). Returns None if invalid."""
        if self.surface is None or index < 0 or index >= len(self.frame_rects):
            return None
        return get_frame(self.surface, self.frame_rects[index])

    def num_frames(self):
        return len(self.frame_rects)

    def is_loaded(self):
        return self.surface is not None
