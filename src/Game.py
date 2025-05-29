import pygame
import enum
import csv
from random import randrange
from src.components import Player, Obstacle, Bird, Ground
import pickle

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
MAX_SPEED = 1000
INIT_SPEED = 400
INCR_SPEED = 20
FRAMERATE = 60
SPAWN_THRESHOLD = 600
ALTERNATE_ANIMATION_TIME = 100
GROUND_Y_POSITION = 400
DINO_X_POSITION = 100
JUMP_ACCELERATION = 700
GRAVITY_ACCELERATION = 40

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

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.sprites = extract_sprites('assets/sprite_sheet.png', 'assets/sprite_locations.csv')

        self.setup()

    def setup(self):
        self.obstacles: list[Obstacle] = []
        self.player = Player(
            self.sprites['dino running first'], self.sprites['dino running second'],
            self.sprites['dino ducking first'], self.sprites['dino ducking second'],
            self.sprites['dino jumping'],
            GROUND_Y_POSITION, DINO_X_POSITION, JUMP_ACCELERATION, GRAVITY_ACCELERATION
        )
        self.ground = Ground(self.sprites['ground'], GROUND_Y_POSITION)

        self.distance_since_last_obstacle = SPAWN_THRESHOLD

        self.speed = INIT_SPEED
        self.running = False

    def _spawn_obstacle(self):
        rng = randrange(0, 7)
        match rng:
            case 0:
                obstacle = Obstacle(self.sprites['small cactus single'], GROUND_Y_POSITION)
            case 1:
                obstacle = Obstacle(self.sprites['small cactus double'], GROUND_Y_POSITION)
            case 2:
                obstacle = Obstacle(self.sprites['small cactus triple'], GROUND_Y_POSITION)
            case 3:
                obstacle = Obstacle(self.sprites['large cactus single'], GROUND_Y_POSITION)
            case 4:
                obstacle = Obstacle(self.sprites['large cactus single'], GROUND_Y_POSITION)
            case 5:
                obstacle = Obstacle(self.sprites['large cactus quadruple'], GROUND_Y_POSITION)
            case 6:
                rng2 = randrange(0, 3)
                obstacle = Bird(self.sprites['bird first'], self.sprites['bird second'], GROUND_Y_POSITION, rng2 * 25)

        self.obstacles.append(obstacle)

    def render(self):
        self.screen.fill("white")

        self.ground.draw(self.screen)

        self.player.draw(self.screen)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        pygame.display.flip()

    def _get_input(self) -> int:
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            return 1

        if keys[pygame.K_DOWN]:
            return 2

        return 0

    def update(self, action: int, dt: float):
        self.player.update(action)

        if any([self.player.rect.colliderect(ob.hitbox) for ob in self.obstacles]):
            self.running = False

        self.ground.move(self.speed, dt)

        self.player.move(dt)

        for obstacle in self.obstacles:
            obstacle.move(self.speed, dt)
        self.obstacles = list(filter(Obstacle.is_on_screen, self.obstacles))

        self.distance_since_last_obstacle += self.speed * dt
        if self.distance_since_last_obstacle >= SPAWN_THRESHOLD:
            self._spawn_obstacle()
            self.distance_since_last_obstacle = 0

        da = INCR_SPEED * dt
        if self.speed + da < MAX_SPEED:
            self.speed += da

    def run(self):
        ALTERNATE_ANIMATION_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(ALTERNATE_ANIMATION_EVENT, ALTERNATE_ANIMATION_TIME)

        dt = 0
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == ALTERNATE_ANIMATION_EVENT:
                    self.player.swap_sprite()
                    for obstacle in self.obstacles:
                        obstacle.swap_sprite()

            self.render()
            action = self._get_input()
            self.update(action, dt)

            dt = self.clock.tick(FRAMERATE) / 1000

        pygame.quit()

    def pool(self) -> list[float]:
        state = []

        state.append(self.player.position)
        state.append(self.player.velocity)
        state.append(self.player.rect.height)
        state.append(self.speed)

        if self.obstacles:
            index = 0 if self.obstacles[0].rect.x > DINO_X_POSITION else 1
            state.append(self.obstacles[index].rect.x)
            state.append(self.obstacles[index].rect.y)
            state.append(self.obstacles[index].rect.width)
            state.append(self.obstacles[index].rect.height)
        else:
            state.append(1300)
            state.append(375)
            state.append(17)
            state.append(35)

        return state

    def quit(self):
        pygame.quit()
