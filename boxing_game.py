import random
import sys

import pygame


SPRITESHEET_PATH = "image_2026-02-12_18-00-04 (2).png"
BACKGROUND_IMAGE_PATH = "ring_background.jpg"
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 650
FPS = 60
ROUND_TIME = 60

FRAME_RECTS = [
    (19, 74, 293, 395),
    (302, 74, 317, 395),
    (609, 73, 317, 396),
    (916, 74, 317, 395),
    (1223, 73, 247, 396),
    (19, 549, 293, 392),
    (302, 548, 317, 393),
    (609, 548, 317, 394),
    (916, 549, 317, 392),
    (1223, 549, 245, 392),
]

IDLE_FRAMES = [0, 1]
ATTACK_FRAMES = [2, 3]
HIT_FRAME = 7
BLOCK_FRAMES = [4, 9]

BACKGROUND_COLOR = (231, 231, 231)
TEXT_COLOR = (30, 30, 30)
PLAYER_COLOR = (220, 20, 60)
ENEMY_COLOR = (45, 45, 45)
HEALTH_BG_COLOR = (170, 170, 170)
HEALTH_BORDER_COLOR = (30, 30, 30)
HEART_IMAGE_PATH = "сердце.png"


class Fighter:
    def __init__(self, frames, x, y, facing_right=True):
        self.frames = frames
        self.x = x
        self.y = y
        self.facing_right = facing_right
        self.health = 100
        self.max_health = 100
        self.state = "idle"
        self.state_time = 0.0
        self.animation_index = 0
        self.last_attack_time = -999.0
        self.hit_cooldown = 0.0
        self.blocking = False

        self.width = 180
        self.height = 240
        self.attack_range = 180

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def can_attack(self, now):
        return now - self.last_attack_time >= 0.65 and self.health > 0

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.state_time = 0.0
            self.animation_index = 0

    def attack(self, now):
        self.last_attack_time = now
        self.blocking = False
        self.set_state("attack")

    def block(self):
        self.blocking = True
        self.set_state("block")

    def stop_block(self):
        self.blocking = False
        if self.state == "block":
            self.set_state("idle")

    def take_hit(self, damage):
        if self.health <= 0:
            return
        if self.blocking:
            damage = max(1, damage // 2)
        self.health = max(0, self.health - damage)
        self.hit_cooldown = 0.18
        self.set_state("hit")

    def update(self, dt):
        self.state_time += dt
        self.hit_cooldown = max(0.0, self.hit_cooldown - dt)

        if self.health <= 0:
            self.set_state("ko")
            return

        if self.state == "attack" and self.state_time >= 0.26:
            if self.blocking:
                self.set_state("block")
            else:
                self.set_state("idle")
        elif self.state == "hit" and self.state_time >= 0.2:
            if self.blocking:
                self.set_state("block")
            else:
                self.set_state("idle")

    def draw(self, surface):
        frame = self.get_current_frame()
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        scaled = pygame.transform.smoothscale(frame, (self.width, self.height))
        surface.blit(scaled, (self.x, self.y))

    def get_current_frame(self):
        if self.state == "attack":
            sequence = ATTACK_FRAMES
            index = int(self.state_time * 12) % len(sequence)
            return self.frames[sequence[index]]
        if self.state == "hit":
            return self.frames[HIT_FRAME]
        if self.state == "block":
            sequence = BLOCK_FRAMES
            index = int(self.state_time * 8) % len(sequence)
            return self.frames[sequence[index]]
        if self.state == "ko":
            return self.frames[BLOCK_FRAMES[-1]]
        sequence = IDLE_FRAMES
        index = int(self.state_time * 3) % len(sequence)
        return self.frames[sequence[index]]


class HealthDisplay:
    def __init__(self, x, y, color, max_health, heart_image=None):
        self.x = x
        self.y = y
        self.color = color
        self.max_health = max_health
        self.bar_width = 360
        self.bar_height = 28
        self.hearts_count = 5
        self.heart_size = 28
        self.heart_gap = 8
        self.heart_image = heart_image

    def draw(self, screen, font, current_health):
        filled_hearts = int(round(self.hearts_count * max(0, current_health) / float(self.max_health)))
        for i in range(self.hearts_count):
            hx = self.x + i * (self.heart_size + self.heart_gap)
            hy = self.y
            if self.heart_image is not None:
                icon = self.heart_image.copy()
                if i >= filled_hearts:
                    icon.set_alpha(80)
                screen.blit(icon, (hx, hy))
            else:
                color = (230, 40, 40) if i < filled_hearts else (115, 115, 115)
                pygame.draw.circle(
                    screen,
                    color,
                    (hx + self.heart_size // 2, hy + self.heart_size // 2),
                    self.heart_size // 2 - 2,
                )


def remove_background(surface, tolerance=24):
    """Делает прозрачным фон, похожий на цвет левого верхнего пикселя."""
    result = surface.convert_alpha()
    bg = result.get_at((0, 0))
    width, height = result.get_size()
    for y in range(height):
        for x in range(width):
            color = result.get_at((x, y))
            if (
                abs(color.r - bg.r) <= tolerance
                and abs(color.g - bg.g) <= tolerance
                and abs(color.b - bg.b) <= tolerance
            ):
                result.set_at((x, y), (color.r, color.g, color.b, 0))
    return result


def load_frames(path):
    image = pygame.image.load(path).convert_alpha()
    frames = []
    for rect in FRAME_RECTS:
        frame = image.subsurface(pygame.Rect(rect)).copy()
        frames.append(remove_background(frame, tolerance=28))
    return frames


def load_background(path):
    image = pygame.image.load(path).convert()
    return pygame.transform.smoothscale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))


def load_heart_icon(path):
    image = pygame.image.load(path).convert_alpha()
    image = remove_background(image, tolerance=20)
    return pygame.transform.smoothscale(image, (28, 28))


def within_attack_range(attacker, defender):
    if attacker.facing_right:
        reach_x = attacker.x + attacker.width + attacker.attack_range
        return reach_x >= defender.x + 30
    reach_x = attacker.x - attacker.attack_range
    return reach_x <= defender.x + defender.width - 30


def draw_ui(screen, font, timer_value, player, enemy, player_health_ui, enemy_health_ui):
    player_health_ui.draw(screen, font, player.health)
    enemy_health_ui.draw(screen, font, enemy.health)

    timer_text = font.render("Время: {}".format(timer_value), True, TEXT_COLOR)
    screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 30))

    help_text = font.render("Управление: A/D - шаг, J - удар, K - блок", True, TEXT_COLOR)
    screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, SCREEN_HEIGHT - 38))


def get_winner_text(player, enemy):
    if player.health > enemy.health:
        return "Победа! Ты чемпион ринга!"
    if enemy.health > player.health:
        return "Поражение. Соперник оказался сильнее."
    return "Ничья! Равный бой."


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Бокс на спрайтах")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 30)
    big_font = pygame.font.SysFont("arial", 46, bold=True)

    try:
        frames = load_frames(SPRITESHEET_PATH)
    except (pygame.error, FileNotFoundError):
        print("Не удалось загрузить {}".format(SPRITESHEET_PATH))
        pygame.quit()
        sys.exit(1)
    try:
        background = load_background(BACKGROUND_IMAGE_PATH)
    except (pygame.error, FileNotFoundError):
        background = None
    try:
        heart_icon = load_heart_icon(HEART_IMAGE_PATH)
    except (pygame.error, FileNotFoundError):
        heart_icon = None

    player = Fighter(frames, 150, 300, facing_right=True)
    enemy = Fighter(frames, 770, 300, facing_right=False)
    player_health_ui = HealthDisplay(40, 30, PLAYER_COLOR, player.max_health, heart_icon)
    enemy_health_ui = HealthDisplay(SCREEN_WIDTH - 400, 30, ENEMY_COLOR, enemy.max_health, heart_icon)

    round_seconds = ROUND_TIME
    elapsed = 0.0
    enemy_action_timer = 0.0
    game_over = False
    winner_text = ""

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        keys = pygame.key.get_pressed()

        if not game_over:
            elapsed += dt
            round_seconds = max(0, ROUND_TIME - int(elapsed))
            if round_seconds == 0:
                game_over = True
                winner_text = get_winner_text(player, enemy)

            speed = 240 * dt
            if keys[pygame.K_a]:
                player.x = max(40, player.x - speed)
            if keys[pygame.K_d]:
                player.x = min(SCREEN_WIDTH - player.width - 40, player.x + speed)

            if keys[pygame.K_k]:
                player.block()
            else:
                player.stop_block()

            now = elapsed
            if keys[pygame.K_j] and player.can_attack(now):
                player.attack(now)
                if within_attack_range(player, enemy):
                    enemy.take_hit(random.randint(8, 13))

            enemy_action_timer -= dt
            if enemy_action_timer <= 0 and enemy.health > 0:
                enemy_action_timer = random.uniform(0.3, 0.9)
                distance = player.x - enemy.x
                if abs(distance) > 170:
                    enemy.x += 120 * dt if distance > 0 else -120 * dt
                else:
                    if random.random() < 0.7 and enemy.can_attack(now):
                        enemy.attack(now)
                        if within_attack_range(enemy, player):
                            player.take_hit(random.randint(6, 12))
                    else:
                        enemy.block()

            if not keys[pygame.K_k]:
                if enemy.state == "block" and random.random() < 0.05:
                    enemy.stop_block()

            player.update(dt)
            enemy.update(dt)

            if player.health <= 0 or enemy.health <= 0:
                game_over = True
                winner_text = get_winner_text(player, enemy)

        if background is not None:
            screen.blit(background, (0, 0))
            shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            shade.fill((255, 255, 255, 36))
            screen.blit(shade, (0, 0))
        else:
            screen.fill(BACKGROUND_COLOR)
        pygame.draw.line(screen, (120, 120, 120), (0, 540), (SCREEN_WIDTH, 540), 3)
        player.draw(screen)
        enemy.draw(screen)
        draw_ui(screen, font, round_seconds, player, enemy, player_health_ui, enemy_health_ui)

        if game_over:
            shade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 110))
            screen.blit(shade, (0, 0))
            text = big_font.render(winner_text, True, (255, 255, 255))
            restart = font.render("R - новая игра, ESC - выход", True, (255, 255, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 255))
            screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 320))

            if keys[pygame.K_r]:
                player = Fighter(frames, 150, 300, facing_right=True)
                enemy = Fighter(frames, 770, 300, facing_right=False)
                round_seconds = ROUND_TIME
                elapsed = 0.0
                enemy_action_timer = 0.0
                game_over = False
                winner_text = ""
            elif keys[pygame.K_ESCAPE]:
                pygame.quit()
                return

        pygame.display.flip()


if __name__ == "__main__":
    main()

