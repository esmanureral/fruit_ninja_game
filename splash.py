
import math
import random
import pygame


class Splash:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.life = 180  # 3 seconds at 60 FPS
        self.max_life = 180
        self.image = self.create_splash_surface(color)
        
    def create_splash_surface(self, color):
        size = 150  # Larger splash
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = (size//2, size//2)
        
        # Main blob
        pygame.draw.circle(surf, color, center, size//4)
        
        # Random droplets/splatters around
        for _ in range(15):
            angle = random.uniform(0, 6.28)
            dist = random.uniform(size//5, size//2.2)
            r = random.uniform(8, 20)
            dx = int(math.cos(angle) * dist)
            dy = int(math.sin(angle) * dist)
            pygame.draw.circle(surf, color, (center[0]+dx, center[1]+dy), int(r))
            
        return surf

    def update(self):
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            self.image.set_alpha(alpha)
            rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, rect)
            
    def is_alive(self):
        return self.life > 0
