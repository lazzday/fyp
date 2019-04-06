import pygame


# Class to extract a sprite from a sprite sheet
class Spritesheet:
    def __init__(self, filename, cols=4, rows=3):
        self.sheet = pygame.image.load(filename).convert_alpha()
        # Crop the image in half
        # self.sheet = self.sheet.subsurface(0, 0, self.sheet.get_rect().width/2, self.sheet.get_rect().height)

        self.cols = cols
        self.rows = rows
        self.totalCellCount = cols * rows

        self.rect = self.sheet.get_rect()
        w = self.cellWidth = int(self.rect.width / cols)
        h = self.cellHeight = int(self.rect.height / rows)
        self.hw, self.hh = self.cellCenter = (int(w / 2), int(h / 2))
        self.cells = list([(index % cols * w, int(index / cols) * h, w, h) for index in range(self.totalCellCount)])
        # self.handle = (-hw, -hh)

    def draw(self, surface, cellIndex, x, y, scale=3):
        cell = self.cells[cellIndex]
        # Scale the sprite if desired
        cellToUse = tuple([i * scale for i in cell])
        scaledSheet = pygame.transform.scale(self.sheet, (
            self.sheet.get_rect().width * scale, self.sheet.get_rect().height * scale))
        # Handle for centred image
        scaledHandle = (-self.hw * scale, -self.hh * scale)
        # Draw the sprite
        surface.blit(scaledSheet, (x + scaledHandle[0], y + scaledHandle[1]), cellToUse)
