import pygame
import os
import multiprocessing
import numpy as np


class DartboardGame(multiprocessing.Process):
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)

    def __init__(self, the_state, queue, SCREEN_WIDTH, SCREEN_HEIGHT):
        super(DartboardGame, self).__init__()
        self.state = the_state
        self.queue = queue
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 1024, 768  # 4:3 aspect ratio
        self.CLOCK = pygame.time.Clock()
        self.FPS = 100

        self.projectile_detector_ready = False
        # self.point_of_impact_coords = tuple()
        self.projectile_detected = False

        self.impact_points = list()
        self.score = 0
        self.score_text_rect = None
        self.attempts = 0

    def on_init(self):
        pygame.init()
        # self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._display_surf = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        # self._running = True

        current_path = os.path.dirname(__file__)
        images_folder = os.path.join(current_path, "images")

        self.bg = pygame.image.load(os.path.join(images_folder, 'background1.png'))
        self.bg = pygame.transform.scale(self.bg, self.size)
        self.impact_x = pygame.image.load(os.path.join(images_folder, 'x.png'))
        self.impact_x = pygame.transform.scale(self.impact_x, (100, 100))

        self._display_surf.fill(self.WHITE)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.state.done = True
            self._running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.unicode == 'q':
                self.state.done = True
                self._running = False

    def on_loop(self):
        if not self.projectile_detector_ready:
            try:
                if self.queue.get(block=False) == "Ready":
                    self.projectile_detector_ready = True
            except:
                # Keep checking
                pass

        else:
            # Check queue for incoming coordinates
            try:
                point_if_impact = self.queue.get(block=False)
                if point_if_impact is not None:
                    print("Read from queue:", point_if_impact)
                    point_of_impact_mm = [point_if_impact[2], point_if_impact[1]]
                    point_of_impact_coords = self.convert_distance_to_coords(point_of_impact_mm)
                    self.impact_points.append(point_of_impact_coords)
                    self.calculate_score(point_of_impact_coords)
                    self.projectile_detected = True
                    self.attempts += 1
                    # self.queue.close()
            except:
                # Do nothing
                pass
                # Note: the display is essential on the x a-xis, so we are only concerned with the points y and z coordinates
                # Therefor we can treat the realworld z coords as the x coords in the animation

    def on_render(self):
        if self.projectile_detector_ready:
            # Draw a green circle in the top left to indicate the projectile detector is ready
            pygame.draw.circle(self._display_surf, self.GREEN, (50, 50), 50)

        pygame.display.update()
        self.CLOCK.tick(self.FPS)
        self.draw_target()
        self.draw_impact_points()
        self.draw_score()

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

    def draw_target(self):
        self._display_surf.fill(self.WHITE)
        center = (int(self.width / 2), int(self.height / 2))

        self.radius_100 = int(self.height * 0.1)
        self.radius_60 = int(self.height * 0.2)
        self.radius_40 = int(self.height * 0.3)
        self.radius_20 = int(self.height * 0.4)

        pygame.draw.circle(self._display_surf, self.BLACK, center, self.radius_20)
        pygame.draw.circle(self._display_surf, self.BLUE, center, self.radius_40)
        pygame.draw.circle(self._display_surf, self.GREEN, center, self.radius_60)
        pygame.draw.circle(self._display_surf, self.RED, center, self.radius_100)

        font = pygame.font.SysFont("comicsansms", 36)
        text_100 = font.render("100", True, self.WHITE)
        text_100_rect = text_100.get_rect(center=(self.width / 2, self.height / 2))
        text_60 = font.render("60", True, self.WHITE)
        text_60_rect = text_60.get_rect(center=(self.width / 2, self.height * 0.35))
        text_40 = font.render("40", True, self.WHITE)
        text_40_rect = text_40.get_rect(center=(self.width / 2, self.height * 0.25))
        text_20 = font.render("20", True, self.WHITE)
        text_20_rect = text_20.get_rect(center=(self.width / 2, self.height * 0.15))

        self._display_surf.blit(text_100, text_100_rect)
        self._display_surf.blit(text_60, text_60_rect)
        self._display_surf.blit(text_40, text_40_rect)
        self._display_surf.blit(text_20, text_20_rect)

    def convert_distance_to_coords(self, point):
        [x, y] = point
        x_coord = np.interp(x, [-self.SCREEN_WIDTH / 2, self.SCREEN_WIDTH / 2], [0, self.width])
        y_coord = np.interp(y, [-self.SCREEN_HEIGHT / 2, self.SCREEN_HEIGHT / 2], [0, self.height])
        point_of_impact_coords = (self.width - x_coord, self.height - y_coord)
        print("Converted to:", point_of_impact_coords)
        return point_of_impact_coords

    def calculate_score(self, point):
        (x, y) = point
        center = (center_x, center_y) = (self.width/2, self.height/2)
        if (x - center_x)**2 + (y - center_y)**2 < self.radius_100**2:
            self.score += 100
        elif (x - center_x)**2 + (y - center_y)**2 < self.radius_60**2:
            self.score += 60
        elif (x - center_x)**2 + (y - center_y)**2 < self.radius_40**2:
            self.score += 40
        elif (x - center_x)**2 + (y - center_y)**2 < self.radius_20**2:
            self.score += 20

    def draw_score(self):
        font = pygame.font.SysFont("comicsansms", 36)
        score_text = font.render("Score: {}".format(self.score), True, self.BLACK)
        self._display_surf.blit(score_text, (self.width - 160, 20))

        attempts_text = font.render("Attempts: {}".format(self.attempts), True, self.BLACK)
        self._display_surf.blit(attempts_text, (self.width - 160, 45))

    def draw_impact_points(self):
        for point in self.impact_points:
            (x, y) = point
            self._display_surf.blit(self.impact_x, (x-self.impact_x.get_width() // 2, y-self.impact_x.get_height() // 2))
