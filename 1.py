import pygame
import random
import time

# Constants
grid_size = 10
cell_size = 50
window_size = grid_size * cell_size
obstacle_count = 30
obstacle_move_interval = 3
fps = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Directions for movement
directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def heuristic(a, b):
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(node, grid):
    """Get valid neighbors for a node."""
    neighbors = []
    for dx, dy in directions:
        nx, ny = node[0] + dx, node[1] + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] != 1:
            neighbors.append((nx, ny))
    return neighbors


def astar(grid, start, end):
    """A* pathfinding algorithm."""
    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        current = min(open_set, key=lambda x: f_score.get(x, float("inf")))

        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        open_set.remove(current)

        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                open_set.add(neighbor)

    return None


def move_obstacles(grid, obstacles):
    """Move obstacles randomly."""
    new_obstacles = set()
    for x, y in obstacles:
        grid[x][y] = 0
        possible_moves = [(x + dx, y + dy) for dx, dy in directions]
        random.shuffle(possible_moves)

        for nx, ny in possible_moves:
            if 0 <= nx < grid_size and 0 <= ny < grid_size and grid[nx][ny] == 0:
                new_obstacles.add((nx, ny))
                grid[nx][ny] = 1
                break

    return new_obstacles


def main():
    pygame.init()
    screen = pygame.display.set_mode((window_size, window_size))
    pygame.display.set_caption("Robot Navigation Simulation")

    clock = pygame.time.Clock()

    # Initialize grid
    grid = [[0] * grid_size for _ in range(grid_size)]

    # Generate random obstacles
    obstacles = set()
    while len(obstacles) < obstacle_count:
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        if (x, y) not in obstacles:
            obstacles.add((x, y))
            grid[x][y] = 1

    # Start and end points
    start = None
    end = None
    path = None
    last_obstacle_move_time = time.time()

    running = True
    while running:
        screen.fill(WHITE)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Get grid position from mouse click
                mouse_x, mouse_y = event.pos
                grid_x, grid_y = mouse_y // cell_size, mouse_x // cell_size

                if grid[grid_x][grid_y] == 0:  # Only allow setting on empty cells
                    if not start:
                        start = (grid_x, grid_y)
                        grid[grid_x][grid_y] = 2
                    elif not end:
                        end = (grid_x, grid_y)
                        grid[grid_x][grid_y] = 3
                        path = astar(grid, start, end)

        # Move obstacles at regular intervals
        if time.time() - last_obstacle_move_time > obstacle_move_interval:
            obstacles = move_obstacles(grid, obstacles)
            if start and end:
                path = astar(grid, start, end)  # Recalculate path
            last_obstacle_move_time = time.time()

        # Recalculate path if it's blocked
        if start and end and path:
            for px, py in path:
                if grid[px][py] == 1:  # Path blocked by an obstacle
                    path = astar(grid, start, end)  # Recalculate path
                    break

        # Draw grid
        for x in range(grid_size):
            for y in range(grid_size):
                rect = pygame.Rect(y * cell_size, x * cell_size, cell_size, cell_size)
                if grid[x][y] == 1:
                    pygame.draw.rect(screen, RED, rect)
                elif start and (x, y) == start:
                    pygame.draw.rect(screen, BLUE, rect)
                elif end and (x, y) == end:
                    pygame.draw.rect(screen, GREEN, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)

        # Draw path
        if path:
            for px, py in path:
                rect = pygame.Rect(py * cell_size, px * cell_size, cell_size, cell_size)
                pygame.draw.rect(screen, YELLOW, rect)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main()
