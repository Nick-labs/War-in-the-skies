import pygame


SIZE = WIDTH, HEIGHT = 640, 480

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

PLANE_SPEED = 5
BULLET_SPEED = 10


# BOMB_SPEED = 3


# c


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((0, 0), (32, 32))  # First tuple is position, second is size.
        self.image = pygame.Surface((32, 32))  # The tuple represent size.
        self.image.fill(WHITE)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

        self.dx = 0
        self.dy = 0

    def update(self):
        self.rect.center = WIDTH // 2 + self.dx * 100, HEIGHT // 2 + self.dy * 100
        # if self.rect.left + self.dx < 0:
        #     self.rect.left = 0
        # elif self.rect.right + self.dx > WIDTH:
        #     self.rect.right = WIDTH
        # elif self.dx > 1 or self.dx < -1:
        #     self.rect.x += self.dx
        #
        # if self.rect.top + self.dy < 0:
        #     self.rect.top = 0
        # elif self.rect.bottom + self.dy > HEIGHT:
        #     self.rect.bottom = HEIGHT
        # elif self.dy > 1 or self.dy < -1:
        #     self.rect.y += self.dy


pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Joystick Game")

plane = Plane()
plane_group = pygame.sprite.Group(plane)

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    axis_0 = joystick.get_axis(0)
    axis_1 = joystick.get_axis(1)

    plane.dx = axis_0
    plane.dy = axis_1

    screen.fill(BLACK)

    plane_group.update()
    plane_group.draw(screen)

    # print(clock.get_fps())
    clock.tick(FPS)

    pygame.display.flip()

pygame.quit()
