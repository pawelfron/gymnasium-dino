import pygame
import enum

class PlayerState(enum.Enum):
    RUNNING = 1
    DUCKING = 2
    JUMPING = 3

class Player:
    def __init__(self, sprite_run1: pygame.Surface, sprite_run2: pygame.Surface, sprite_duck1: pygame.Surface, sprite_duck2: pygame.Surface, sprite_jump: pygame.Surface, ground_position: int, x_position: int, jump_acc: int, gravity_acc: int):
        self.sprite_run1 = sprite_run1
        self.sprite_run2 = sprite_run2
        self.sprite_duck1 = sprite_duck1
        self.sprite_duck2 = sprite_duck2
        self.sprite_jump = sprite_jump
    
        self.height_difference = sprite_run1.get_height() - sprite_duck2.get_height()
        self.x_position = x_position
        self.base_position = ground_position - self.sprite_run1.get_height() + 13
        self.jump_acc = jump_acc
        self.gravity_acc = gravity_acc

        self.position = self.base_position
        self.velocity = 0
        self.state = PlayerState.RUNNING

        self.sprite = sprite_run1
        self.other_sprite = sprite_run2
        self.rect = self.sprite.get_rect(topleft=(self.x_position, self.base_position))
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.sprite, self.rect)

    def _switch_rect_size(self, is_ducking: bool):
        offset = self.height_difference if is_ducking else 0
        self.rect = self.sprite.get_rect(topleft=(self.x_position, self.position + offset))
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)

    def update(self, action: int):
        match self.state:
            case PlayerState.RUNNING:
                if action == 1:
                    self.state = PlayerState.JUMPING
                    self.velocity += self.jump_acc

                    self.sprite = self.sprite_jump
                    self.other_sprite = self.sprite_jump

                elif action == 2:
                    self.state = PlayerState.DUCKING

                    self.sprite = self.sprite_duck1
                    self.other_sprite = self.sprite_duck2
                    self._switch_rect_size(True)

            case PlayerState.JUMPING:
                if self.position >= self.base_position:
                    self.state = PlayerState.RUNNING
                    self.velocity = 0

                    self.sprite = self.sprite_run1
                    self.other_sprite = self.sprite_run2
                else:
                    self.velocity -= self.gravity_acc

            case PlayerState.DUCKING:
                if not action == 2:
                    self.state = PlayerState.RUNNING

                    self.sprite = self.sprite_run1
                    self.other_sprite = self.sprite_run2
                    self._switch_rect_size(False)

    def move(self, dt: float):
        dy = int(self.velocity * dt)

        self.position -= dy
        self.rect.y -= dy
        self.hitbox.y -= dy

        if self.position > self.base_position:
            self.position = self.base_position
            self.rect.y = self.base_position
            self.hitbox.y = self.base_position

    def swap_sprite(self):
        temp = self.sprite
        self.sprite = self.other_sprite
        self.other_sprite = temp
