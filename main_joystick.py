import pygame
import random
from config import *


# import math


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
                bullets_group.add(Bullet(plane.rect.centerx - 1, plane.rect.top + 2, (4, 8), 40, is_enemy=False))
                self.gun_ammo -= 1
                self.last_gun_fire = now
            if now - self.last_m_gun_fire > 100 and guns[1] and self.m_gun_ammo > 0:
                m_gun_sound.play()
                bullets_group.add(Bullet(plane.rect.left + 30, plane.rect.top + 24, (3, 6), 10, is_enemy=False))
                bullets_group.add(Bullet(plane.rect.left + 65, plane.rect.top + 24, (3, 6), 10, is_enemy=False))
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

    def respawn(self, xy=(WIDTH // 2, HEIGHT // 2)):
        # enemies_group.empty() # Когда теряем жизнь, удаляем всех врагов с экрана
        self.lifes -= 1
        self.hp = 100

        self.rect.x = xy[0]
        self.rect.y = xy[1]

    def update(self):
        hit_list = pygame.sprite.spritecollide(self, bullets_group, False)
        if hit_list:
            for bul in hit_list:
                if bul.is_enemy:
                    bul.kill()
            self.hp -= sum(map(lambda bul: bul.damage * bul.is_enemy, hit_list))

        if self.hp <= 0:
            self.respawn()

        if self.lifes <= 0:
            self.alife = False
            self.hp = 0
            self.kill()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, size, damage, is_enemy=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface(size)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x

        self.damage = damage

        self.is_enemy = is_enemy

    def update(self):
        if self.is_enemy:
            self.rect.y += BULLET_SPEED
        else:
            self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
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


class Enemy(pygame.sprite.Sprite):
    def __init__(self, hp, pos):
        pygame.sprite.Sprite.__init__(self)
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.center = pos
        # self.rect.topleft = pos

        self.last_fire = 0
        self.fire_time = 400
        self.damage = 10

        self.dx = 1
        self.dy = 0

        self.hp = hp

    def set_params(self, hp, dx, dy, damage, fire_time):
        self.hp = hp

        self.fire_time = fire_time
        self.damage = damage

        self.dx = dx
        self.dy = dy

    def load_image(self):
        self.image = pygame.image.load("data/plane.png")
        self.image = pygame.transform.flip(self.image, False, True)

    def set_dx_dy(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def move(self):
        pass

    def fire(self):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_time:
            gun_sound.play()
            bullets_group.add(Bullet(self.rect.centerx - 1, self.rect.bottom + 4, (4, 8), self.damage, is_enemy=True))
            self.last_fire = now

    def draw_hp(self):
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.left + 20, self.rect.top - 24, self.rect.width - 40, 21))
        gui.tprint(screen, f'HP: {self.hp}', (self.rect.x + 23, self.rect.y - 24))

    def check_collision(self):
        hit_list = pygame.sprite.spritecollide(self, bullets_group, False)
        if hit_list:
            for bul in hit_list:
                if not bul.is_enemy:
                    bul.kill()
            self.hp -= sum(map(lambda bul: bul.damage * (not bul.is_enemy), hit_list))

        plane_collision = pygame.sprite.spritecollide(self, plane_group, False)
        if plane_collision:
            self.hp = 0
            plane_collision[0].respawn()
            self.kill()

    def update(self):
        global score
        self.move()
        self.fire()
        self.check_collision()
        self.draw_hp()

        if self.hp <= 0:
            self.kill()


class EnemyPlane1(Plane):
    def __init__(self, hp, pos, dx, dy, damage, fire_time):
        Enemy.__init__(self, hp, pos)
        self.hp = hp
        self.hp_p = self.hp // 10
        self.fire_time = fire_time
        self.damage = damage
        self.dx = dx
        self.dy = dy

    def load_image(self):
        self.image = pygame.image.load("data/plane.png")
        self.image = pygame.transform.flip(self.image, False, True)

    def set_dx_dy(self, dx, dy):
        self.dx = dx
        self.dy = dy

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            # self.rect.right = WIDTH - 1
            self.dx = -self.dx

    def fire(self):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_time:
            gun_sound.play()
            bullets_group.add(Bullet(self.rect.centerx - 1, self.rect.bottom + 4, (4, 8), self.damage, is_enemy=True))
            self.last_fire = now

    def draw_hp(self):
        pygame.draw.rect(screen, (255, 255, 255), (self.rect.left + 20, self.rect.top - 24, self.rect.width - 20, 23))
        gui.tprint(screen, f'HP: ' + '|' * min(self.hp // self.hp_p + 1, 10), (self.rect.x + 23, self.rect.y - 24))

    def check_collision(self):
        hit_list = pygame.sprite.spritecollide(self, bullets_group, False)
        if hit_list:
            for bul in hit_list:
                if not bul.is_enemy:
                    bul.kill()
            self.hp -= sum(map(lambda bul: bul.damage * (not bul.is_enemy), hit_list))

        plane_collision = pygame.sprite.spritecollide(self, plane_group, False)
        if plane_collision:
            self.hp = 0
            plane_collision[0].respawn()
            self.kill()

    def update(self):
        global score

        self.move()
        self.fire()
        self.check_collision()
        self.draw_hp()

        if self.hp <= 0:
            self.kill()
            score += self.hp_p * self.damage // 10


def start_screen():
    smallfont = pygame.font.SysFont(None, 30)
    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.quit()
                pygame.joystick.quit()
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                wait = False
        screen.fill(WHITE)
        text = smallfont.render("Press any key to start game", True, (0, 0, 0))
        screen.blit(text, (320, 240))
        pygame.display.update()
        clock.tick(15)


def end_screen(score):
    smallfont = pygame.font.SysFont(None, 30)
    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.quit()
                pygame.joystick.quit()
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                pygame.mixer.quit()
                pygame.joystick.quit()
                pygame.quit()
                quit()
        screen.fill(WHITE)
        text1 = smallfont.render("You died", True, (0, 0, 0))
        text2 = smallfont.render("Your score is: " + str(score), True, (0, 0, 0))
        text3 = smallfont.render("Press any key to quit", True, (0, 0, 0))
        screen.blit(text1, (320, 240))
        screen.blit(text2, (320, 270))
        screen.blit(text3, (320, 300))
        pygame.display.update()
        clock.tick(15)


pygame.init()
pygame.joystick.init()
pygame.mixer.init()

print(pygame.joystick.get_count())

gui = GUI()

joystick = pygame.joystick.Joystick(0)

clock = pygame.time.Clock()

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Joystick Game")

# screen.blit(pygame.image.load("data/fon.jpg", SIZE))


start_screen()

background1 = pygame.transform.scale(pygame.image.load("data/water.jpg"), SIZE)
background2 = background1.__copy__()

background1_rect = background1.get_rect()

background2_rect = background2.get_rect()
background2_rect.y -= HEIGHT

plane = Plane()
plane_group = pygame.sprite.Group(plane)

enemies_group = pygame.sprite.Group()

bullets_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()

score = 0

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
        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(RELOAD_BUTTON):
                plane.add_ammo(gun_ammo=30, m_gun_ammo=100, bombs=2)
            # if joystick.get_button(10):
            #     for i in range(5 - len(enemies_group)):
            #         print(i)
            #         enemies_group.add(EnemyPlane1(100, (100, 100), i + 1, 0, (i + 1) * 5, 100 * (i + 1)))
    if not enemies_group:
        for i in range(random.randint(1, 5)):
            plane.add_ammo(gun_ammo=30, m_gun_ammo=100, bombs=2)
            score += 50
            enemies_group.add(EnemyPlane1(random.randint(1, 5) * 100,
                                          (random.randint(100, WIDTH - 100),
                                           50 + random.randint(1, 3) * 50),
                                          random.randint(1, 5), 0, random.randint(1, 5) * 5,
                                          random.randint(2, 5) * 100))

    axis_0 = joystick.get_axis(0)
    axis_1 = joystick.get_axis(1)
    axis_3 = joystick.get_axis(3)

    plane.move(axis_0 * 5 * (1 - axis_3),
               axis_1 * 5 * (1 - axis_3))

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

    enemies_group.update()
    enemies_group.draw(screen)

    plane_group.update()
    plane_group.draw(screen)

    pygame.draw.rect(screen, (0, 0, 0), (0, HEIGHT - 122, 110, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT - 117, 105, HEIGHT))

    gui.tprint(screen, f'SPEED: {(-axis_3 + 1) * 50:.0f}', (3, HEIGHT - 112))
    gui.tprint(screen, f'AMMO1: {plane.gun_ammo}', (3, HEIGHT - 89))
    gui.tprint(screen, f'AMMO2: {plane.m_gun_ammo}', (3, HEIGHT - 66))
    gui.tprint(screen, f'BOMBS: {plane.bombs}', (3, HEIGHT - 43))
    gui.tprint(screen, f'SCORE: {score}', (3, HEIGHT - 20))

    pygame.draw.rect(screen, (0, 0, 0), (WIDTH - 110, HEIGHT - 55, WIDTH, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (WIDTH - 105, HEIGHT - 50, WIDTH, HEIGHT))

    gui.tprint(screen, f'HP: {plane.hp}', (WIDTH - 100, HEIGHT - 46))
    gui.tprint(screen, '☺ ' * plane.lifes + '☻ ' * (3 - plane.lifes), (WIDTH - 103, HEIGHT - 26))

    print(clock.get_fps())
    clock.tick(FPS)

    pygame.display.flip()

    if not plane.alife:
        end_screen(score)

# end_screen(score)
pygame.mixer.quit()
pygame.joystick.quit()
pygame.quit()
