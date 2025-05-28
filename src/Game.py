import pygame
import enum
import csv
from random import randrange
from src.Obstacles import Obstacle, Bird

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
MAX_SPEED = 1000
INIT_SPEED = 400
INCR_SPEED = 10
FRAMERATE = 60
SPAWN_THRESHOLD = 500
ALTERNATE_ANIMATION_TIME = 100
GROUND_PLACEMENT = 400
DINO_PLACEMENT = 100

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

class PlayerState(enum.Enum):
    RUNNING = 1
    DUCKING = 2
    JUMPING = 3

class PlayerAction(enum.Enum):
    NOTHING = 1
    DUCK = 2
    JUMP = 3

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.player_state = PlayerState.RUNNING
        self.sprites = extract_sprites('assets/sprite_sheet.png', 'assets/sprite_locations.csv')
        self.second_frame = False
        self.obstacles: list[Obstacle] = []

        self.base_height = GROUND_PLACEMENT - self.sprites['dino running first'].get_height() + 13
        self.player_position = self.base_height
        self.height_difference = self.sprites['dino running first'].get_height() - self.sprites['dino ducking first'].get_height()
        self.velocity = 0

        self.ground_x1 = 0
        self.ground_x2 = self.sprites['ground'].get_width()
        self.ground_width = self.sprites['ground'].get_width()


        self.offset_height = False
        self.player_sprite = self.sprites['dino running first']
        self.player_rect = self.player_sprite.get_rect(topleft=(DINO_PLACEMENT, self.player_position + (self.height_difference if self.offset_height else 0)))
        self.player_rect = pygame.Rect(self.player_rect.x + 5, self.player_rect.y + 5, self.player_rect.width - 10, self.player_rect.height - 10)

        self.distance_since_last_obstacle = 0

        self.speed = INIT_SPEED

        self.running = False

    def _spawn_obstacle(self):
        rng = randrange(0, 7)
        match rng:
            case 0:
                obstacle = Obstacle(self.sprites['small cactus single'], GROUND_PLACEMENT)
            case 1:
                obstacle = Obstacle(self.sprites['small cactus double'], GROUND_PLACEMENT)
            case 2:
                obstacle = Obstacle(self.sprites['small cactus triple'], GROUND_PLACEMENT)
            case 3:
                obstacle = Obstacle(self.sprites['large cactus single'], GROUND_PLACEMENT)
            case 4:
                obstacle = Obstacle(self.sprites['large cactus single'], GROUND_PLACEMENT)
            case 5:
                obstacle = Obstacle(self.sprites['large cactus quadruple'], GROUND_PLACEMENT)
            case 6:
                rng2 = randrange(0, 3)
                obstacle = Bird(self.sprites['bird first'], self.sprites['bird second'], GROUND_PLACEMENT, rng2 * 25)
        
        self.obstacles.append(obstacle)

    def render(self):
        self.screen.fill("white")

        if self.player_state == PlayerState.RUNNING:
            self.player_sprite = self.sprites['dino running first'] if self.second_frame else self.sprites['dino running second']
            self.offset_height = False
        elif self.player_state == PlayerState.DUCKING:
            self.player_sprite = self.sprites['dino ducking first'] if self.second_frame else self.sprites['dino ducking second']
            self.offset_height = True
        else:
            self.player_sprite = self.sprites['dino jumping']
            self.offset_height = False

        self.screen.blit(self.sprites['ground'], (self.ground_x1, GROUND_PLACEMENT))
        self.screen.blit(self.sprites['ground'], (self.ground_x2, GROUND_PLACEMENT))

        self.screen.blit(self.player_sprite, (DINO_PLACEMENT, self.player_position + (self.height_difference if self.offset_height else 0)))

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        pygame.display.flip()

    def _get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            return PlayerAction.JUMP
        
        if keys[pygame.K_DOWN]:
            return PlayerAction.DUCK
        
        return PlayerAction.NOTHING

    def update(self, action: PlayerAction, dt: float):
        match self.player_state:
            case PlayerState.RUNNING:
                if action == PlayerAction.JUMP:
                    self.velocity += 700
                    self.player_state = PlayerState.JUMPING
                elif action == PlayerAction.DUCK:
                    self.player_state = PlayerState.DUCKING

            case PlayerState.JUMPING:
                if self.player_position >= self.base_height:
                    self.player_state = PlayerState.RUNNING
                    self.velocity = 0
                else:
                    self.velocity -= 40

            case PlayerState.DUCKING:
                if not action == PlayerAction.DUCK:
                    self.player_state = PlayerState.RUNNING

        self.player_rect = self.player_sprite.get_rect(topleft=(DINO_PLACEMENT, self.player_position + (self.height_difference if self.offset_height else 0)))
        self.player_rect = pygame.Rect(self.player_rect.x + 5, self.player_rect.y + 5, self.player_rect.width - 10, self.player_rect.height - 10)

        if any([self.player_rect.colliderect(obstacle.hitbox) for obstacle in self.obstacles]):
            self.running = False

        for obstacle in self.obstacles:
            obstacle.move(self.speed, dt)
        self.obstacles = list(filter(Obstacle.is_on_screen, self.obstacles))


        self.ground_x1 -= int(self.speed * dt)
        self.ground_x2 -= int(self.speed * dt)

        # Reset position when off screen
        if self.ground_x1 <= - self.ground_width:
            self.ground_x1 = self.ground_x2 + self.ground_width
        if self.ground_x2 <= - self.ground_width:
            self.ground_x2 = self.ground_x1 + self.ground_width

        self.player_position -= self.velocity * dt
        if self.player_position > self.base_height:
            self.player_position = self.base_height
        
        self.distance_since_last_obstacle += self.speed * dt

        if self.distance_since_last_obstacle >= SPAWN_THRESHOLD:
            self._spawn_obstacle()
            self.distance_since_last_obstacle = 0

        if self.speed < MAX_SPEED:
            self.speed += INCR_SPEED * dt

    def run(self):
        self.clock = pygame.time.Clock()
        ALTERNATE_ANIMATION_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(ALTERNATE_ANIMATION_EVENT, ALTERNATE_ANIMATION_TIME)

        dt = 0
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == ALTERNATE_ANIMATION_EVENT:
                    self.second_frame = not self.second_frame
                    for obstacle in self.obstacles:
                        obstacle.swap_sprite()

            self.render()
            action = self._get_input()
            self.update(action, dt)

            dt = self.clock.tick(FRAMERATE) / 1000

        pygame.quit()

    def quit(self):
        pygame.quit()