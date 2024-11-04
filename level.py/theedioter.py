import pygame
import json
import os

# Constants
TILE_SIZE = 20  # Tile size
GRID_WIDTH = 50
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200
GRAVITY = 0.5  # Gravity force

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)      # Deadly tile
GREEN = (0, 255, 0)    # Good tile
BLUE = (0, 0, 255)      # Spawn point tile
GRAY = (150, 150, 150)  # Sidebar background

# Tile types
TILES = {
    0: WHITE,   # Empty
    1: RED,     # Deadly tile
    2: GREEN,   # Good tile
    3: BLUE     # Spawn point
}

# Initialize Pygame
pygame.init()
screen_width = TILE_SIZE * GRID_WIDTH + SIDEBAR_WIDTH  # Width of the window
screen_height = TILE_SIZE * GRID_HEIGHT  # Height of the window
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Game Editor with Player")
clock = pygame.time.Clock()

# Grid to hold the tile map
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
scroll_x = 0
scroll_y = 0

# Player attributes
player_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]  # Start in the middle of the grid
spawn_point = player_pos[:]  # Initialize spawn point
game_state = "edit"  # Possible states: "edit" or "play"
vertical_speed = 0  # Player's vertical speed
gravity_enabled = True  # Is gravity enabled?

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            tile_color = TILES[grid[y][x]]
            pygame.draw.rect(screen, tile_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, BLACK, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)

def draw_player():
    player_x, player_y = player_pos
    pygame.draw.rect(screen, BLUE, (player_x * TILE_SIZE, player_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def draw_sidebar():
    pygame.draw.rect(screen, GRAY, (screen_width - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, screen_height))
    button_rect = pygame.Rect(screen_width - SIDEBAR_WIDTH + 10, 10, SIDEBAR_WIDTH - 20, 40)
    pygame.draw.rect(screen, BLACK, button_rect)
    font = pygame.font.Font(None, 36)
    text = font.render("Player", True, WHITE)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    gravity_button_rect = pygame.Rect(screen_width - SIDEBAR_WIDTH + 10, 60, SIDEBAR_WIDTH - 20, 40)
    pygame.draw.rect(screen, BLACK, gravity_button_rect)
    gravity_text = font.render("Gravity: On" if gravity_enabled else "Gravity: Off", True, WHITE)
    gravity_text_rect = gravity_text.get_rect(center=gravity_button_rect.center)
    screen.blit(gravity_text, gravity_text_rect)

    play_stop_button_rect = pygame.Rect(screen_width - SIDEBAR_WIDTH + 10, 110, SIDEBAR_WIDTH - 20, 40)
    pygame.draw.rect(screen, BLACK, play_stop_button_rect)
    play_stop_text = font.render("Play" if game_state == "edit" else "Stop", True, WHITE)
    play_stop_text_rect = play_stop_text.get_rect(center=play_stop_button_rect.center)
    screen.blit(play_stop_text, play_stop_text_rect)

def save_grid(filename):
    with open(filename, 'w') as f:
        json.dump(grid, f)

def load_grid(filename):
    global grid, spawn_point
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            grid = json.load(f)

    spawn_point[:] = [GRID_WIDTH // 2, GRID_HEIGHT // 2]  # Default to center

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] == 3:  # Check for blue tile
                spawn_point[:] = [x, y]  # Update spawn point
                break

def reset_player():
    global player_pos, vertical_speed
    player_pos = spawn_point[:]  # Reset to spawn point
    vertical_speed = 0  # Reset vertical speed

def check_ground_collision():
    player_x, player_y = player_pos
    player_y = int(player_y)

    # Check the tile directly below the player
    if player_y + 1 < GRID_HEIGHT:
        # Check if the tile below is solid (ground or green)
        if grid[player_y + 1][player_x] in [1, 2]:  # 1: Red (deadly), 2: Green (good)
            player_pos[1] = player_y + 1  # Snap to the ground
            return True
    return False

def apply_gravity():
    global vertical_speed, gravity_enabled
    player_x, player_y = player_pos
    player_y = int(player_y)

    if gravity_enabled:
        vertical_speed += GRAVITY  # Increase speed downwards
        player_pos[1] += vertical_speed  # Move the player down

        # Check for collisions after applying gravity
        if check_ground_collision():
            vertical_speed = 0  # Stop falling
        else:
            # Check if the player is falling onto a green tile
            if player_y + 1 < GRID_HEIGHT:
                if grid[player_y + 1][player_x] == 2:  # Green tile below
                    player_pos[1] = player_y  # Snap player to the top of the tile
                    vertical_speed = 0  # Stop falling
                    gravity_enabled = False  # Disable gravity while on green tile
                elif grid[player_y + 1][player_x] == 0:  # Empty tile below
                    gravity_enabled = True  # Ensure gravity is enabled if falling through empty space

def main():
    global game_state, gravity_enabled
    running = True
    current_tile = 1  # Start with Tile 1

    load_grid("level.json")  # Load existing grid if available

    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_player()
        draw_sidebar()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Check if the Player button was clicked
                if x >= screen_width - SIDEBAR_WIDTH:
                    if y >= 10 and y <= 50:  # Player button area
                        print("Player button clicked!")  # Placeholder action

                    # Check if the Gravity button was clicked
                    if y >= 60 and y <= 100:  # Gravity button area
                        gravity_enabled = not gravity_enabled  # Toggle gravity
                        print("Gravity toggled:", "On" if gravity_enabled else "Off")

                    # Check if the Play/Stop button was clicked
                    if y >= 110 and y <= 150:  # Play/Stop button area
                        if game_state == "edit":
                            game_state = "play"
                            reset_player()  # Reset player to spawn point
                            print("Entering play mode.")
                        else:
                            game_state = "edit"
                            reset_player()  # Reset player to spawn point
                            print("Exiting play mode. Returning to edit mode.")

                else:
                    if game_state == "edit":  # Only allow tile placement in edit mode
                        grid_x = x // TILE_SIZE
                        grid_y = y // TILE_SIZE

                        # Place or delete the tile
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            if grid[grid_y][grid_x] == 0:
                                grid[grid_y][grid_x] = current_tile
                            else:
                                grid[grid_y][grid_x] = 0

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_tile = 1  # Red tile
                elif event.key == pygame.K_2:
                    current_tile = 2  # Green tile
                elif event.key == pygame.K_3:
                    current_tile = 3  # Blue tile (spawn point)
                elif event.key == pygame.K_s:
                    save_grid("level.json")
                elif event.key == pygame.K_l:
                    load_grid("level.json")

        if game_state == "play":
            keys = pygame.key.get_pressed()
            new_x, new_y = player_pos[0], player_pos[1]

            # Handle horizontal movement
            if keys[pygame.K_LEFT] and new_x > 0:  # Move left
                new_x -= 1
            if keys[pygame.K_RIGHT] and new_x < GRID_WIDTH - 1:  # Move right
                new_x += 1

            # Check if the player can move to the new horizontal position
            if grid[int(new_y)][int(new_x)] == 2:  # Can't move through green tiles
                new_x = player_pos[0]
            elif grid[int(new_y)][int(new_x)] == 1:  # Deadly tile
                reset_player()  # Reset player to spawn point

            # Update player position if valid
            player_pos[0] = int(new_x)

            # Apply gravity
            apply_gravity()

            # Reset player if they fall off the bottom of the screen
            if player_pos[1] >= GRID_HEIGHT:
                reset_player()  # Reset player to spawn point if they fall off the screen

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
