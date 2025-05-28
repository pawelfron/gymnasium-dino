import pygame

class Ground:
    def __init__(self, sprite: pygame.Surface, y: int):
        self.sprite = sprite
        self.y = y
        self.width = self.sprite.get_width()
        self.x1 = 0
        self.x2 = self.width

    def draw(self, screen: pygame.Surface):
        screen.blit(self.sprite, (self.x1, self.y))
        screen.blit(self.sprite, (self.x2, self.y))

    def move(self, speed: float, dt: float):
        dx = int(speed * dt)
        self.x1 -= dx
        self.x2 -= dx

        if self.x1 <= - self.width:
            self.x1 = self.x2 + self.width
        if self.x2 <= - self.width:
            self.x2 = self.x1 + self.width
