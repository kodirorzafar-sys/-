import pygame
import random
from typing import List, Tuple, Optional

# --- Configuration ---
SCREEN_WIDTH, SCREEN_HEIGHT = 600, 800
GRID_SIZE = 8
CELL_SIZE = 50
GRID_OFFSET_X = (SCREEN_WIDTH - (GRID_SIZE * CELL_SIZE)) // 2
GRID_OFFSET_Y = 100

# Colors
COLORS = {
    "BG": (18, 18, 18),
    "GRID": (40, 40, 40),
    "BLOCK_1": (255, 69, 58),
    "BLOCK_2": (50, 215, 75),
    "BLOCK_3": (10, 132, 255),
    "BLOCK_4": (255, 214, 10),
    "SHADOW": (60, 60, 60)
}

SHAPES = [
    [(0, 0), (0, 1), (1, 0), (1, 1)],  # Square
    [(0, 0), (0, 1), (0, 2)],          # I-3
    [(0, 0), (1, 0), (2, 0)],          # I-3 horizontal
    [(0, 0), (0, 1), (1, 1)],          # L-small
    [(0, 0)],                          # Dot
]

class Block:
    def __init__(self, shape: List[Tuple[int, int]], color: Tuple[int, int, int], pos: pygame.Vector2):
        self.shape = shape
        self.color = color
        self.pos = pos
        self.original_pos = pygame.Vector2(pos)
        self.dragging = False
        self.active = True

    def draw(self, surface: pygame.Surface, scale: float = 1.0):
        if not self.active: return
        for dx, dy in self.shape:
            rect = pygame.Rect(
                self.pos.x + dx * CELL_SIZE * scale,
                self.pos.y + dy * CELL_SIZE * scale,
                CELL_SIZE * scale - 2,
                CELL_SIZE * scale - 2
            )
            pygame.draw.rect(surface, self.color, rect, border_radius=4)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.blocks = self.spawn_blocks()
        self.dragging_block: Optional[Block] = None
        self.score = 0
        self.running = True

    def spawn_blocks(self) -> List[Block]:
        new_blocks = []
        for i in range(3):
            shape = random.choice(SHAPES)
            color = random.choice([COLORS["BLOCK_1"], COLORS["BLOCK_2"], COLORS["BLOCK_3"], COLORS["BLOCK_4"]])
            pos = pygame.Vector2(80 + i * 160, 600)
            new_blocks.append(Block(shape, color, pos))
        return new_blocks

    def check_lines(self):
        to_clear_rows = []
        to_clear_cols = []

        for r in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for c in range(GRID_SIZE)):
                to_clear_rows.append(r)
        
        for c in range(GRID_SIZE):
            if all(self.grid[r][c] is not None for r in range(GRID_SIZE)):
                to_clear_cols.append(c)

        for r in to_clear_rows:
            for c in range(GRID_SIZE): self.grid[r][c] = None
        for c in to_clear_cols:
            for r in range(GRID_SIZE): self.grid[r][c] = None
            
        if to_clear_rows or to_clear_cols:
            self.score += (len(to_clear_rows) + len(to_clear_cols)) * 10

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                m_pos = pygame.mouse.get_pos()
                for b in self.blocks:
                    if b.active and pygame.Rect(b.pos.x, b.pos.y, 100, 100).collidepoint(m_pos):
                        b.dragging = True
                        self.dragging_block = b
                        break

            if event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_block:
                    self.try_place_block(self.dragging_block)
                    self.dragging_block.dragging = False
                    self.dragging_block.pos = pygame.Vector2(self.dragging_block.original_pos)
                    self.dragging_block = None
                    
                    if all(not b.active for b in self.blocks):
                        self.blocks = self.spawn_blocks()

    def try_place_block(self, block: Block):
        gx = round((block.pos.x - GRID_OFFSET_X) / CELL_SIZE)
        gy = round((block.pos.y - GRID_OFFSET_Y) / CELL_SIZE)

        can_place = True
        for dx, dy in block.shape:
            nx, ny = gx + dx, gy + dy
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or self.grid[ny][nx]:
                can_place = False
                break
        
        if can_place:
            for dx, dy in block.shape:
                self.grid[gy + dy][gx + dx] = block.color
            block.active = False
            self.check_lines()

    def update(self):
        if self.dragging_block:
            m_pos = pygame.mouse.get_pos()
            self.dragging_block.pos = pygame.Vector2(m_pos[0] - CELL_SIZE/2, m_pos[1] - CELL_SIZE/2)

    def draw(self):
        self.screen.fill(COLORS["BG"])
        
        # Draw Grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(GRID_OFFSET_X + c * CELL_SIZE, GRID_OFFSET_Y + r * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(self.screen, COLORS["GRID"], rect, border_radius=2)
                if self.grid[r][c]:
                    pygame.draw.rect(self.screen, self.grid[r][c], rect, border_radius=4)

        # Draw UI/Blocks
        for b in self.blocks:
            if b != self.dragging_block:
                b.draw(self.screen, scale=0.8)
        
        if self.dragging_block:
            self.dragging_block.draw(self.screen, scale=1.0)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    Game().run()