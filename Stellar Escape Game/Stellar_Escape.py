import pygame
import random
import time


pygame.init()

WIDTH, HEIGHT = 600, 400
FPS = 30
TIMER_LIMIT = 45  
BLOCK_SIZE = 20
MAZE_WIDTH = WIDTH // BLOCK_SIZE
MAZE_HEIGHT = HEIGHT // BLOCK_SIZE

# Colors
BACKGROUND_COLOR = (55, 151, 119)  # #379777
STAR_COLOR = (244, 206, 20)  # #F4CE14
START_END_COLOR = (69, 71, 75)  # #45474B
TIMER_COLOR = (245, 247, 248)  # #F5F7F8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GOLD = (255, 223, 0)  # Color for stars
GREY = (169, 169, 169)  # Color for moving obstacles
BALL_COLOR = (255, 235, 85)  # #FFEB55 (bright yellow for ball)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Game")


font = pygame.font.SysFont('arial', 24)
large_font = pygame.font.SysFont('arial', 36)


pygame.mixer.init()
win_sound = pygame.mixer.Sound("win_sound.wav")
lose_sound = pygame.mixer.Sound("lose_sound.wav")
background_music = pygame.mixer.Sound("background_music.wav")
background_music.set_volume(0.1)
background_music.play(-1, 0, 5000)


def generate_maze():
    maze = [[1] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]  
    stack = []
    visited = [[False] * MAZE_WIDTH for _ in range(MAZE_HEIGHT)]  

    def check_neighbors(x, y):
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAZE_WIDTH and 0 <= ny < MAZE_HEIGHT and not visited[ny][nx]:
                neighbors.append((nx, ny))
        return neighbors

    def carve(x, y):
        visited[y][x] = True
        neighbors = check_neighbors(x, y)
        random.shuffle(neighbors)

        for nx, ny in neighbors:
            if not visited[ny][nx]:
                maze[ny][nx] = 0
                maze[(y + ny) // 2][(x + nx) // 2] = 0  
                stack.append((x, y))
                carve(nx, ny)

    carve(1, 1) 
    maze[MAZE_HEIGHT - 2][MAZE_WIDTH - 2] = 0  
    return maze

def draw_maze(maze):
    for y in range(MAZE_HEIGHT):
        for x in range(MAZE_WIDTH):
            if maze[y][x] == 1:
                pygame.draw.rect(screen, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def draw_player(player_x, player_y):
    pygame.draw.circle(screen, BALL_COLOR, (player_x * BLOCK_SIZE + BLOCK_SIZE // 2, player_y * BLOCK_SIZE + BLOCK_SIZE // 2), BLOCK_SIZE // 2)

def draw_exit(exit_x, exit_y):
    pygame.draw.rect(screen, START_END_COLOR, (exit_x * BLOCK_SIZE, exit_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    end_text = font.render("End", True, WHITE)
    screen.blit(end_text, (exit_x * BLOCK_SIZE + BLOCK_SIZE // 4, exit_y * BLOCK_SIZE + BLOCK_SIZE // 4))

def draw_start(start_x, start_y):
    pygame.draw.rect(screen, START_END_COLOR, (start_x * BLOCK_SIZE, start_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
    start_text = font.render("Start", True, WHITE)
    screen.blit(start_text, (start_x * BLOCK_SIZE + BLOCK_SIZE // 4, start_y * BLOCK_SIZE + BLOCK_SIZE // 4))

def draw_star(star_x, star_y):
    pygame.draw.circle(screen, STAR_COLOR, (star_x * BLOCK_SIZE + BLOCK_SIZE // 2, star_y * BLOCK_SIZE + BLOCK_SIZE // 2), BLOCK_SIZE // 4)

def draw_moving_obstacle(obstacle_x, obstacle_y):
    pygame.draw.rect(screen, GREY, (obstacle_x * BLOCK_SIZE, obstacle_y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

def game_loop():
    maze = generate_maze()
    player_x, player_y = 1, 1  
    exit_x, exit_y = MAZE_WIDTH - 2, MAZE_HEIGHT - 2
    start_x, start_y = 1, 1  
    
    stars = set()
    while len(stars) < 8:  
        star_x = random.randint(1, MAZE_WIDTH - 2)
        star_y = random.randint(1, MAZE_HEIGHT - 2)
        if maze[star_y][star_x] == 0: 
            stars.add((star_x, star_y))
    
    collected_stars = 0  

    obstacles = []
    for _ in range(3): 
        obs_x = random.randint(1, MAZE_WIDTH - 2)
        obs_y = random.randint(1, MAZE_HEIGHT - 2)
        if maze[obs_y][obs_x] == 0: 
            obstacles.append([obs_x, obs_y, random.choice([1, -1]), random.randint(5, 10)])  

    clock = pygame.time.Clock()
    start_time = time.time()
    running = True
    game_over = False
    reached_exit = False

    while running:
        elapsed_time = time.time() - start_time
        remaining_time = TIMER_LIMIT - int(elapsed_time)

        if remaining_time <= 0:
            game_over = True
            running = False

        screen.fill(BACKGROUND_COLOR) 
        draw_maze(maze)
        
        
        draw_player(player_x, player_y)
        draw_start(start_x, start_y)  
        draw_exit(exit_x, exit_y)  
        for star in stars:
            draw_star(star[0], star[1])

        
        for obstacle in obstacles:
            draw_moving_obstacle(obstacle[0], obstacle[1])

        
        counter_text = font.render(f"Time Remaining: {remaining_time}s", True, TIMER_COLOR)  
        screen.blit(counter_text, (WIDTH // 2 - counter_text.get_width() // 2, 20))

       
        if (player_x, player_y) in stars:
            stars.remove((player_x, player_y)) 
            collected_stars += 1  

       
        if player_x == exit_x and player_y == exit_y and collected_stars == 8:
            reached_exit = True
            game_over = True
            running = False

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

       
        keys = pygame.key.get_pressed()
        if player_x > 0 and keys[pygame.K_LEFT] and maze[player_y][player_x - 1] == 0:
            player_x -= 1
        if player_x < MAZE_WIDTH - 1 and keys[pygame.K_RIGHT] and maze[player_y][player_x + 1] == 0:
            player_x += 1
        if player_y > 0 and keys[pygame.K_UP] and maze[player_y - 1][player_x] == 0:
            player_y -= 1
        if player_y < MAZE_HEIGHT - 1 and keys[pygame.K_DOWN] and maze[player_y + 1][player_x] == 0:
            player_y += 1

        
        for obstacle in obstacles:
            obs_x, obs_y, direction, speed = obstacle
            if obs_x + direction < 1 or obs_x + direction >= MAZE_WIDTH - 1:
                direction *= -1 
            obstacle[0] = obs_x + direction
            obstacle[2] = direction

        for obstacle in obstacles:
            if player_x == obstacle[0] and player_y == obstacle[1]:
                game_over = True
                running = False

        pygame.display.flip()
        clock.tick(FPS)

    if game_over:
        if reached_exit:
            win_sound.play()
            result_text = large_font.render("You Win!", True, GREEN)
        else:
            lose_sound.play()
            result_text = large_font.render("Game Over!", True, RED)

        screen.fill(WHITE)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 3))
        pygame.display.flip()
        pygame.time.wait(3000)

game_loop()

pygame.quit()
