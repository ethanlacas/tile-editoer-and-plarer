import pygame
import json
import os

# Constants
TILE_SIZE = 40
GRID_WIDTH = 50
GRID_HEIGHT = 20
SCREEN_WIDTH = 800
SCREEN_HEIGHT = GRID_HEIGHT * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)      # Deadly tile
GREEN = (0, 255, 0)    # Good tile (blocker)
BLUE = (0, 0, 255)      # Spawn point tile

# Initialize Pygame 
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Play")
clock = pygame.time.Clock()

# Load grid from file
def load_grid(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return None

def draw_grid(screen, grid, camera_x, camera_y):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile_color = {
                0: WHITE,
                1: RED,
                2: GREEN,
                3: BLUE,
            }[grid[y][x]]
            # Adjust the tile position based on the camera
            pygame.draw.rect(screen, tile_color, ((x - camera_x) * TILE_SIZE, (y - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, ((x - camera_x) * TILE_SIZE, (y - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def find_spawn_point(grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 3:  # Spawn point
                return [x, y]
    return None

def main():
    level_file = input("Enter the level filename (e.g., level.json): ")
    grid = load_grid(level_file)

    if grid is None:
        print(f"Could not load level file: {level_file}. Exiting.")
        return

    player_pos = find_spawn_point(grid)
    if player_pos is None:
        print("No spawn point found! Please create a level with a spawn point.")
        return

    # Camera position
    camera_x = player_pos[0]
    camera_y = player_pos[1]

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid(screen, grid, camera_x, camera_y)

        # Draw player
        pygame.draw.rect(screen, BLUE, ((player_pos[0] - camera_x) * TILE_SIZE, (player_pos[1] - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        new_pos = player_pos[:]  # Create a copy of the player's position

        if keys[pygame.K_LEFT] and new_pos[0] > 0:
            new_pos[0] -= 1
        if keys[pygame.K_RIGHT] and new_pos[0] < GRID_WIDTH - 1:
            new_pos[0] += 1
        if keys[pygame.K_UP] and new_pos[1] > 0:
            new_pos[1] -= 1
        if keys[pygame.K_DOWN] and new_pos[1] < GRID_HEIGHT - 1:
            new_pos[1] += 1

        # Check for collisions with tiles
        if grid[new_pos[1]][new_pos[0]] != 2:  # Blocker check (tile type 2)
            player_pos = new_pos  # Only update if not a blocker

        # Update camera position
        camera_x = player_pos[0] - SCREEN_WIDTH // (2 * TILE_SIZE)
        camera_y = player_pos[1] - SCREEN_HEIGHT // (2 * TILE_SIZE)

        # Check for collisions with deadly tiles
        if grid[player_pos[1]][player_pos[0]] == 1:  # Red tile
            print("Hit a deadly tile! Game Over.")
            player_pos = find_spawn_point(grid)  # Reset to spawn point

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
