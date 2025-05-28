import pygame

class Obstacle:
    def __init__(self, sprite: pygame.Surface, ground_height: int):
        self.sprite = sprite
        self.rect = self.sprite.get_rect(topleft=(1200 + 100, ground_height - self.sprite.get_height() + 10))
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.sprite, self.rect)

    def move(self, speed, dt):
        self.rect.x -= int(speed * dt)
        self.hitbox.x -= int(speed * dt)

    def is_on_screen(self):
        return self.rect.right > 0

    def swap_sprite(self):
        pass

class Bird(Obstacle):
    def __init__(self, sprite1: pygame.Surface, sprite2: pygame.Surface, ground_height: int, fly_height: int):
        self.sprite = sprite1
        self.other_sprite = sprite2
        self.rect = self.sprite.get_rect(topleft=(1200 + 100, ground_height - self.sprite.get_height() - fly_height + 10))
        self.hitbox = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width - 10, self.rect.height - 10)

    def swap_sprite(self):
        temp = self.sprite
        self.sprite = self.other_sprite
        self.other_sprite = temp
