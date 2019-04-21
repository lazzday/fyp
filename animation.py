import pygame
import random
from pygame.locals import *
from animationUtil import Spritesheet
import os
import multiprocessing


class Animation(multiprocessing.Process):

    def __init__(self, the_state, queue):
        super(Animation, self).__init__()
        self.state = the_state
        self.queue = queue
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 800, 800
        self.CLOCK = pygame.time.Clock()
        self.FPS = 100
        # List of usable sprite sheets and sizes
        self.sprites = [("salamence_sprite.png", 8, 8),
                        ("blastoise_sprite.png", 13, 5),
                        ("charizard_sprite.png", 9, 7),
                        ("greninja_sprite.png", 23, 3),
                        ("dragonite_sprite.png", 9, 9),
                        ("pigeot_sprite.png", 21, 3)]

        # self.point_of_impact_coords = tuple()
        self.projectile_detected = False

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        # self._running = True

        current_path = os.path.dirname(__file__)
        images_folder = os.path.join(current_path, "images")

        # Randomly select which sprite to appear
        spriteToUse = self.sprites[random.randint(0, 5)]
        # Render the sprite from the sprite sheet
        self.spriteIndex = 0
        self.sprite = Spritesheet(os.path.join(images_folder, spriteToUse[0]), cols=spriteToUse[1], rows=spriteToUse[2])
        self.bg = pygame.image.load(os.path.join(images_folder, 'background1.png'))
        self.bg = pygame.transform.scale(self.bg, self.size)
        self.impact_x = pygame.image.load(os.path.join(images_folder, 'x.png'))
        self.impact_x = pygame.transform.scale(self.impact_x, (100, 100))

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.state.done = True
            self._running = False

    def on_loop(self):
        # Check queue for incoming coordinates
        try:
            point_if_impact = self.queue.get(block=False)
            if point_if_impact is not None:
                # self.point_x = point_if_impact[0]
                print("Read from queue:", point_if_impact)
                self.point_of_impact_coords = [point_if_impact[2], point_if_impact[1]]
                self.projectile_detected = True
                self.queue.close()
        except:
            # Do nothing
            pass

            # Note: the display is essential on the x a-xis, so we are only concerned with the points y and z coordinates
            # Therefor we can treat the realworld z coords as the x coords in the animation


    def on_render(self):
        self.sprite.draw(self._display_surf, self.spriteIndex % self.sprite.totalCellCount, self.size[0] / 2,
                         self.size[1] / 2)
        if self.projectile_detected == True:
            self._display_surf.blit(self.impact_x, (0, 0))

        pygame.display.update()
        self.spriteIndex += 1
        self.CLOCK.tick(self.FPS)
        self._display_surf.blit(self.bg, (0, 0))

    def on_cleanup(self):
        pygame.display.quit()
        pygame.quit()

    def run(self):
        if not self.on_init():
            print("here")
            # self._running = False

        while not self.state.done:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
        return

