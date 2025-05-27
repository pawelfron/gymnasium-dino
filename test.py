# Example file showing a circle moving on screen
import pygame

MAX_SPEED = 500
FRAMERATE = 60

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
speed = 10

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")

    pygame.draw.circle(screen, "red", player_pos, 40)

    keys = pygame.key.get_pressed()
    dx = speed * dt
    if keys[pygame.K_w]:
        player_pos.y -= dx
    if keys[pygame.K_s]:
        player_pos.y += dx
    if keys[pygame.K_a]:
        player_pos.x -= dx
    if keys[pygame.K_d]:
        player_pos.x += dx

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(FRAMERATE) / 1000
    if speed < MAX_SPEED:
        speed += 1

pygame.quit()