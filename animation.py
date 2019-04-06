import pygame
import random
from pygame.locals import *
from animationUtil import Spritesheet
import os


class Animation:

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 800, 800

        self.CLOCK = pygame.time.Clock()
        self.FPS = 60
        # List of usable sprite sheets and sizes
        self.sprites = [("salamence_sprite.png", 8, 8),
                        ("blastoise_sprite.png", 13, 5),
                        ("charizard_sprite.png", 9, 7),
                        ("greninja_sprite.png", 23, 3),
                        ("dragonite_sprite.png", 9, 9),
                        ("pigeot_sprite.png", 21, 3)]

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True

        current_path = os.path.dirname(__file__)
        images_folder = os.path.join(current_path, "images")

        # Randomly select which sprite to appear
        spriteToUse = self.sprites[random.randint(0, 5)]
        # Render the sprite from the sprite sheet
        self.spriteIndex = 0
        self.sprite = Spritesheet(os.path.join(images_folder, spriteToUse[0]), cols=spriteToUse[1], rows=spriteToUse[2])
        self.bg = pygame.image.load(os.path.join(images_folder, 'background1.png'))
        self.bg = pygame.transform.scale(self.bg, self.size)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):

        self.sprite.draw(self._display_surf, self.spriteIndex % self.sprite.totalCellCount, self.size[0] / 2,
                         self.size[1] / 2)
        pygame.display.update()
        self.spriteIndex += 1
        self.CLOCK.tick(self.FPS)
        self._display_surf.blit(self.bg, (0, 0))

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        if not self.on_init():
            self._running = False

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == "__main__":
    theApp = Animation()
    theApp.on_execute()
