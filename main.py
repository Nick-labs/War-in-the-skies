import pygame
import random
import math

SIZE = WIDTH, HEIGHT = 1024, 768

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BACKGROUND_SPEED = 2

PLANE_SPEED = 5
BULLET_SPEED = 12

START_LIFES = 3

START_GUN_AMMO = 40
START_M_GUN_AMMO = 200
START_BOMBS = 2

MAX_GUN_AMMO = 100
MAX_M_GUN_AMMO = 400
MAX_BOMBS = 2

GUN_BUTTON = 0
M_GUN_BUTTON = 1
BOMB_BUTTON = 2
RELOAD_BUTTON = 3


class GUI:
    def __init__(self):
        self.font = pygame.font.SysFont('arial', 18)
        self.line_height = 15

    def tprint(self, screen, text, xy):
        text_bitmap = self.font.render(text, True, BLACK)
        screen.blit(text_bitmap, xy)


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("data/plane.png")
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

        self.alife = True

        self.hp = 100
        self.lifes = START_LIFES

        self.bombs = START_BOMBS
        self.gun_ammo = START_GUN_AMMO
        self.m_gun_ammo = START_M_GUN_AMMO

        self.last_gun_fire = 0
        self.last_m_gun_fire = 0
        self.last_bomb = -5000

        self.dx = 0
        self.dy = 0

    def move(self, dx, dy):
        self.dx, self.dy = dx, dy

        if self.rect.left + self.dx < 0:
            self.rect.left = 0
            self.hp -= 40
            self.rect.x = WIDTH // 2
            self.rect.y = HEIGHT // 2
        elif self.rect.right + self.dx > WIDTH:
            self.rect.right = WIDTH
        elif self.dx > 1 or self.dx < -1:
            self.rect.x += self.dx

        if self.rect.top + self.dy < 0:
            self.rect.top = 0
        elif self.rect.bottom + self.dy > HEIGHT:
            self.rect.bottom = HEIGHT
        elif self.dy > 1 or self.dy < -1:
            self.rect.y += self.dy

    def fire(self, guns):
        if self.alife:
            now = pygame.time.get_ticks()
            if now - self.last_gun_fire > 400 and guns[0] and self.gun_ammo > 0:
                gun_sound.play()
                bullets_group.add(Bullet(plane.rect.centerx - 1, plane.rect.top + 2, (4, 8), is_enemy=False))
                self.gun_ammo -= 1
                self.last_gun_fire = now
            if now - self.last_m_gun_fire > 100 and guns[1] and self.m_gun_ammo > 0:
                m_gun_sound.play()
                bullets_group.add(Bullet(plane.rect.left + 30, plane.rect.top + 24, (3, 6), is_enemy=False))
                bullets_group.add(Bullet(plane.rect.left + 65, plane.rect.top + 24, (3, 6), is_enemy=False))
                self.m_gun_ammo -= 2
                self.last_m_gun_fire = now

    def bomb(self):
        if self.alife and self.bombs > 0:
            now = pygame.time.get_ticks()
            if now - self.last_bomb > 5000:  # время задержки сбрасывания бомбы в миллисекундах
                bomb_group.add(Bomb(plane.rect.centerx - 1, plane.rect.top + 34, plane.dy))
                self.bombs -= 1
                self.last_bomb = now

    def add_ammo(self, gun_ammo=0, m_gun_ammo=0, bombs=0):
        reload_sound.play()
        self.gun_ammo = min(MAX_GUN_AMMO, self.gun_ammo + gun_ammo)
        self.m_gun_ammo = min(MAX_M_GUN_AMMO, self.m_gun_ammo + m_gun_ammo)
        self.bombs = min(MAX_BOMBS, self.bombs + bombs)

    def update(self):
        if self.hp <= 0:
            self.lifes -= 1
            self.hp = 100
        if self.lifes <= 0:
            self.kill()
            self.alife = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, size, is_enemy=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x

        self.is_enemy = is_enemy

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.top < 0:
            self.kill()


class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((8, 12))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = max(-speed, 3)
        self.boom_time = 0

    def update(self):
        self.rect.y -= self.speed
        self.speed *= 0.95

        if self.speed < 0.1:
            if not self.boom_time:
                self.speed = 0
                self.image = pygame.image.load("data/bomb_explosion.png")
                bomb_explosion_sound.play()
                self.rect.x -= 47
                self.rect.y -= 35
                self.boom_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.boom_time >= 1500:
                self.kill()
            else:
                self.rect.y += BACKGROUND_SPEED


pygame.init()
pygame.joystick.init()
pygame.mixer.init()

joystick = pygame.joystick.Joystick(0)

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Joystick Game")

background1 = pygame.transform.scale(pygame.image.load("data/water.jpg"), SIZE)
background2 = background1.__copy__()

background1_rect = background1.get_rect()

background2_rect = background2.get_rect()
background2_rect.y -= HEIGHT

plane = Plane()
plane_group = pygame.sprite.Group(plane)

bullets_group = pygame.sprite.Group()

bomb_group = pygame.sprite.Group()

gui = GUI()

clock = pygame.time.Clock()

pygame.mixer.music.load("data/sounds/background_music.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.3)

gun_sound = pygame.mixer.Sound("data/sounds/gun.ogg")
m_gun_sound = pygame.mixer.Sound("data/sounds/m_gun.ogg")
bomb_explosion_sound = pygame.mixer.Sound("data/sounds/bomb_explosion.ogg")
reload_sound = pygame.mixer.Sound("data/sounds/reload.ogg")

pygame.mixer.Sound("data/sounds/plane.ogg").play(-1)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYBUTTONDOWN and joystick.get_button(RELOAD_BUTTON):
            plane.add_ammo(gun_ammo=30, m_gun_ammo=100, bombs=2)

    axis_0 = joystick.get_axis(0)
    axis_1 = joystick.get_axis(1)
    axis_3 = joystick.get_axis(3)

    plane.move(axis_0 * 5 * -(axis_3 - 1),
               axis_1 * 5 * -(axis_3 - 1))
    guns = joystick.get_button(GUN_BUTTON), joystick.get_button(M_GUN_BUTTON)
    if guns:
        plane.fire(guns)

    if joystick.get_button(BOMB_BUTTON):
        plane.bomb()

    screen.fill(BLACK)

    screen.blit(background1, background1_rect)
    screen.blit(background2, background2_rect)

    if background1_rect.y < HEIGHT - BACKGROUND_SPEED:
        background1_rect.y += BACKGROUND_SPEED
    else:
        background1_rect.y = -HEIGHT

    if background2_rect.y < HEIGHT - BACKGROUND_SPEED:
        background2_rect.y += BACKGROUND_SPEED
    else:
        background2_rect.y = -HEIGHT

    bomb_group.update()
    bomb_group.draw(screen)

    bullets_group.update()
    bullets_group.draw(screen)

    plane_group.update()
    plane_group.draw(screen)

    pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 122, 110, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 117, 105, HEIGHT))

    gui.tprint(screen, f'SPEED: {(-axis_3 + 1) * 50:.0f}', (3, HEIGHT - 112))
    gui.tprint(screen, f'AMMO1: {plane.gun_ammo}', (3, HEIGHT - 89))
    gui.tprint(screen, f'AMMO2: {plane.m_gun_ammo}', (3, HEIGHT - 66))
    gui.tprint(screen, f'BOMBS: {plane.bombs}', (3, HEIGHT - 43))

    pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 110, HEIGHT - 55, WIDTH, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 105, HEIGHT - 50, WIDTH, HEIGHT))

    gui.tprint(screen, f'HP: {plane.hp}', (WIDTH - 100, HEIGHT - 46))
    gui.tprint(screen, '☺ ' * plane.lifes + '☻ ' * (3 - plane.lifes), (WIDTH - 103, HEIGHT - 26))

    # print(clock.get_fps())
    clock.tick(FPS)

    pygame.display.flip()

pygame.mixer.quit()
pygame.joystick.quit()
pygame.quit()
