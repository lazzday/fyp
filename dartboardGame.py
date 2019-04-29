'''
Simple dartboard style game to demonstrate the accuracy of the projectile detector.
Receives the expected point of impact via multiprocessing queue as soon as it is available,
then displays its position relative to the dartboard.
'''

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
        self.projectile_detected = False

        self.impact_points = list()
        self.score = 0
        self.score_text_rect = None
        self.attempts = 0

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.FULLSCREEN)

        current_path = os.path.dirname(__file__)
        images_folder = os.path.join(current_path, "images")

        # self.bg = pygame.image.load(os.path.join(images_folder, 'background1.png'))
        # self.bg = pygame.transform.scale(self.bg, self.size)
        self.impact_x = pygame.image.load(os.path.join(images_folder, 'x.png'))
        self.impact_x = pygame.transform.scale(self.impact_x, (100, 100))

        self._display_surf.fill(self.WHITE)
        self.plot_load_delay = 0
        self.last_throw_plot = None
        self.loading_counter = 0
        self.avg_vel = 0

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
                    self.avg_vel = point_if_impact[3]
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
        if not self.projectile_detector_ready:
            # Draw a green circle in the top left to indicate the projectile detector is ready
            self.draw_loading_screen()
        else:
            self.draw_target()
            self.draw_impact_points()
            self.draw_score()
            self.draw_plot()

        pygame.display.update()
        self.CLOCK.tick(self.FPS)

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
        # Function to draw the dartboard target
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
        #  Function to convert the point of impact from real world measurements (mm) to pixel coordinates
        [x, y] = point
        x_coord = np.interp(x, [-self.SCREEN_WIDTH / 2, self.SCREEN_WIDTH / 2], [0, self.width])
        y_coord = np.interp(y, [-self.SCREEN_HEIGHT / 2, self.SCREEN_HEIGHT / 2], [0, self.height])
        point_of_impact_coords = (self.width - x_coord, self.height - y_coord)
        print("Converted to:", point_of_impact_coords)
        return point_of_impact_coords

    def calculate_score(self, point):
        # Function to calculate the current "Score", from where the projectile impacts the target
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
        # Function to draw then current score, the total attempts and the velocity of the previous throw.
        font = pygame.font.SysFont("courier", 28)
        score_text = font.render("Score: {}".format(self.score), True, self.BLACK)
        self._display_surf.blit(score_text, (self.width - 240, 20))

        attempts_text = font.render("Attempts: {}".format(self.attempts), True, self.BLACK)
        self._display_surf.blit(attempts_text, (self.width - 240, 45))

        font = pygame.font.SysFont("courier", 36)
        velocity_text = font.render("Vel: {:.2f}m/s".format(self.avg_vel), True, self.BLACK)
        self._display_surf.blit(velocity_text, (20, self.height-40))

    def draw_impact_points(self):
        # Function to draw an 'X' at the calculated point of impact.
        for point in self.impact_points:
            (x, y) = point
            self._display_surf.blit(self.impact_x, (x-self.impact_x.get_width() // 2, y-self.impact_x.get_height() // 2))

    def draw_plot(self):
        # Function to draw the 3d plot of the last throw's trajectory on the display
        if self.attempts > 0:
            current_path = os.path.dirname(__file__)
            plots_folder = os.path.join(current_path, "images/plots")
            plot = os.path.join(plots_folder, 'throw{}.png'.format(self.attempts-1))
            if os.path.isfile(plot):
                try:
                    self.last_throw_plot = pygame.image.load(plot)
                    self.last_throw_plot = pygame.transform.scale(self.last_throw_plot, (int(self.width*0.45), int(self.height*0.45)))
                    self._display_surf.blit(self.last_throw_plot, (int(self.width*0.66), int(self.height * 0.63)))
                except:
                    # Image is not available yet, do nothing
                    pass

    def draw_loading_screen(self):
        # Function to draw and display the loading screen while the game awaits
        # the ready command from the projectile detector
        self.loading_counter += 1
        loading_surf = pygame.Surface((self.width, self.height))
        loading_surf.fill(self.RED)
        font = pygame.font.SysFont("couriernew", 64)
        title_text = font.render("Projectile Detection Demo", True, self.WHITE)
        title_text_rect = title_text.get_rect(center=(int(self.width / 2), int(self.height / 2)))
        font = pygame.font.SysFont("couriernew", 54)
        loading_text = font.render("LOADING   ", True, self.BLUE)
        if self.loading_counter < 60:
            loading_text = font.render("LOADING   ", True, self.BLUE)
        elif self.loading_counter < 120:
            loading_text = font.render("LOADING.  ", True, self.BLUE)
        elif self.loading_counter < 180:
            loading_text = font.render("LOADING.. ", True, self.BLUE)
        elif self.loading_counter < 240:
            loading_text = font.render("LOADING...", True, self.BLUE)
        else:
            self.loading_counter = 0

        loading_text_rect = loading_text.get_rect(center=(int(self.width / 2), int(self.height*0.66)))
        loading_surf.blit(title_text, title_text_rect)
        loading_surf.blit(loading_text, loading_text_rect)

        self._display_surf.blit(loading_surf, (0, 0))
