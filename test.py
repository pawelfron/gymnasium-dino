# Example file showing a circle moving on screen
import pygame
import csv
import os
import enum
from random import randrange

MAX_SPEED = 500
FRAMERATE = 60
MAX_JUMP_HEIGHT = 100
ASSETS_DIR = 'assets'
SPRITE_SHEET_FILE = os.path.join(ASSETS_DIR, 'sprite_sheet.png')
SPRITE_LOCATIONS_FILE = os.path.join(ASSETS_DIR, 'sprite_locations.csv')

ANIMATION_TIME = 6
INITIAL_JUMP_FORCE = 1500
CONTINUED_JUMP_FORCE = 700
DOWN_FORCE = 800
GRAVITY = 400
GROUND_PLACEMENT = 400
DINO_PLACEMENT = 100

class PlayerState(enum.Enum):
    RUNNING = 1
    DUCKING = 2
    JUMPING = 3
    FREEFALL = 4

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1200, 600))

def extract_sprites(sheet_filename: str, locations_filename: str) -> dict[str, pygame.Surface]:
    sprites = dict()
    
    sprite_sheet = pygame.image.load(sheet_filename).convert_alpha()
    with open(locations_filename, 'r') as locations:
        reader = csv.reader(locations)
        next(reader) # skip headers
        for row in reader:
            name = row[0]
            x = int(row[1])
            y = int(row[2])
            width = int(row[3])
            height = int(row[4])

            sprite = pygame.Surface((width, height), pygame.SRCALPHA)
            sprite.blit(sprite_sheet, (0, 0), (x, y, width, height))

            sprites[name] = sprite

    return sprites

sprites = extract_sprites(SPRITE_SHEET_FILE, SPRITE_LOCATIONS_FILE)
clock = pygame.time.Clock()
running = True
dt = 0
# speed = 10

obstacle_img = sprites['small cactus single']
obstacle_speed = 400
obstacles: list[tuple[pygame.Surface, pygame.Rect]] = []

def spawn_obstacle():
    rng = randrange(0, 7)
    match rng:
        case 0:
            obstacle_img = sprites['small cactus single']
        case 1:
            obstacle_img = sprites['small cactus double']
        case 2:
            obstacle_img = sprites['small cactus triple']
        case 3:
            obstacle_img = sprites['large cactus single']
        case 4:
            obstacle_img = sprites['large cactus single']
        case 5:
            obstacle_img = sprites['large cactus quadruple']
        case 6:
            obstacle_img = sprites['bird first'] if second_frame else sprites['bird second']
            rng2 = randrange(0, 3)
            y_pos = 40 + rng2 * 25

    if rng != 6:
        y_pos = obstacle_img.get_height()

    obstacle_rect = obstacle_img.get_rect(topleft=(1200 + 100, GROUND_PLACEMENT - y_pos + 5))
    obstacle_rect = pygame.Rect(obstacle_rect.x + 5, obstacle_rect.y + 5, obstacle_rect.width - 10, obstacle_rect.height - 10)
    obstacles.append((obstacle_img, obstacle_rect))
    

height_difference = sprites['dino running first'].get_height() - sprites['dino ducking first'].get_height()
base_height = GROUND_PLACEMENT - sprites['dino running first'].get_height() + 13
max_height = base_height - MAX_JUMP_HEIGHT
player_pos = pygame.Vector2(DINO_PLACEMENT, base_height)
player_state = PlayerState.RUNNING

second_frame = False
offset_height = False

ground_img = sprites['ground']
ground_x1 = 0
ground_x2 = ground_img.get_width()
ground_y = GROUND_PLACEMENT
ground_speed = 400


SPAWN_OBSTACLE = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_OBSTACLE, 1500)  # every 1.5 seconds
ALTERNATE_ANIMATION = pygame.USEREVENT + 2
pygame.time.set_timer(ALTERNATE_ANIMATION, 100)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_OBSTACLE:
            spawn_obstacle()
        elif event.type == ALTERNATE_ANIMATION:
            second_frame = not second_frame

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    if player_state == PlayerState.RUNNING:
        player_sprite = sprites['dino running first'] if second_frame else sprites['dino running second']
        offset_height = False
    elif player_state == PlayerState.DUCKING:
        player_sprite = sprites['dino ducking first'] if second_frame else sprites['dino ducking second']
        offset_height = True
    else:
        player_sprite = sprites['dino jumping']
        offset_height = False

    player_rect = player_sprite.get_rect(topleft=(player_pos.x, player_pos.y + (height_difference if offset_height else 0)))
    player_rect = pygame.Rect(player_rect.x + 5, player_rect.y + 5, player_rect.width - 10, player_rect.height - 10)

    # Draw ground
    screen.blit(ground_img, (ground_x1, ground_y))
    screen.blit(ground_img, (ground_x2, ground_y))

    screen.blit(player_sprite, (player_pos.x, player_pos.y + (height_difference if offset_height else 0)))

    # Draw obstacles
    for sprite, hitbox in obstacles:
        screen.blit(sprite, hitbox)

    # Check for collisions
    if any(player_rect.colliderect(hitbox) for _, hitbox in obstacles):
        break

    # In your game loop:
    for _, hitbox in obstacles:
        hitbox.x -= int(obstacle_speed * dt)

    # Remove obstacles that are off screen
    obstacles = [ob for ob in obstacles if ob[1].right > 0]

    ground_x1 -= int(ground_speed * dt)
    ground_x2 -= int(ground_speed * dt)

    # Reset position when off screen
    if ground_x1 <= -ground_img.get_width():
        ground_x1 = ground_x2 + ground_img.get_width()
    if ground_x2 <= -ground_img.get_width():
        ground_x2 = ground_x1 + ground_img.get_width()


    keys = pygame.key.get_pressed()
    match player_state:
        case PlayerState.RUNNING:
            if keys[pygame.K_UP]:
                dy = CONTINUED_JUMP_FORCE * dt
                player_pos.y = player_pos.y - dy if player_pos.y - dy >= max_height else max_height
                player_state = PlayerState.JUMPING
            elif keys[pygame.K_DOWN]:
                player_state = PlayerState.DUCKING

        case PlayerState.DUCKING:
            if keys[pygame.K_UP]:
                dy = CONTINUED_JUMP_FORCE * dt
                player_pos.y = player_pos.y - dy if player_pos.y - dy >= max_height else max_height
                player_state = PlayerState.JUMPING
            elif not keys[pygame.K_DOWN]:
                player_state = PlayerState.RUNNING

        case PlayerState.JUMPING:
            if player_pos.y == max_height:
                player_state = PlayerState.FREEFALL
            elif keys[pygame.K_UP]:
                dy = CONTINUED_JUMP_FORCE * dt
                player_pos.y = player_pos.y - dy if player_pos.y - dy >= max_height else max_height
            else:
                player_state = PlayerState.FREEFALL

        case PlayerState.FREEFALL:
            if player_pos.y == base_height:
                player_state = PlayerState.RUNNING
            elif keys[pygame.K_DOWN]:
                dy = DOWN_FORCE * dt
                player_pos.y = player_pos.y + dy if player_pos.y + dy <= base_height else base_height
            else:
                dy = GRAVITY * dt
                player_pos.y = player_pos.y + dy if player_pos.y + dy <= base_height else base_height

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(FRAMERATE) / 1000
    # if speed < MAX_SPEED:
    #     speed += 1

pygame.quit()