import pygame
import random
import sys
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

PADDLE_WIDTH = 15
PADDLE_HEIGHT = 100
PADDLE_SPEED = 400 # pixels per second
PADDLE_OFFSET = 30

BALL_SIZE = 15
BALL_START_SPEED = 300 # pixels per second
BALL_SPEED_MULTIPLIER = 1.05
MAX_BOUNCE_ANGLE = math.radians(60) # 60 degrees

MAX_SCORE = 12

# --- Game States ---
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_SERVE = 3

class Paddle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.y_float = float(y)
    
    def move(self, direction, dt):
        self.y_float += direction * PADDLE_SPEED * dt
        self.rect.y = int(self.y_float)
        
        # Clamping
        if self.rect.top < 0:
            self.rect.top = 0
            self.y_float = float(self.rect.y)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.y_float = float(self.rect.y)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

class Ball:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.rect = pygame.Rect(x - BALL_SIZE//2, y - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.vx = 0.0
        self.vy = 0.0
        self.speed = BALL_START_SPEED

    def serve(self, direction_x):
        self.rect.center = (self.start_x, self.start_y)
        self.x_float = float(self.rect.x)
        self.y_float = float(self.rect.y)
        self.speed = BALL_START_SPEED
        
        angle = random.uniform(-math.pi/4, math.pi/4) # Random angle between -45 and 45 degrees
        self.vx = self.speed * math.cos(angle) * direction_x
        self.vy = self.speed * math.sin(angle)

    def update(self, dt):
        self.x_float += self.vx * dt
        self.y_float += self.vy * dt
        self.rect.x = int(self.x_float)
        self.rect.y = int(self.y_float)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pong Kombat v1.0")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 36, bold=True)
        self.large_font = pygame.font.SysFont("Arial", 72, bold=True)
        
        self.paddle1 = Paddle(PADDLE_OFFSET, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.paddle2 = Paddle(SCREEN_WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2)
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        self.score1 = 0
        self.score2 = 0
        self.state = STATE_MENU
        self.serve_timer = 0
        self.serve_direction = 1 # 1 for right, -1 for left
        self.winner_text = ""

    def reset_game(self):
        self.score1 = 0
        self.score2 = 0
        self.paddle1.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle1.y_float = float(self.paddle1.rect.y)
        self.paddle2.rect.y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle2.y_float = float(self.paddle2.rect.y)
        self.state = STATE_SERVE
        self.serve_timer = 1.0 # 1 second pause
        self.serve_direction = random.choice([1, -1])
        self.ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def handle_input(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                elif self.state == STATE_GAME_OVER:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()

        keys = pygame.key.get_pressed()
        
        if self.state in [STATE_PLAYING, STATE_SERVE]:
            # Player 1 (W/S)
            if keys[pygame.K_w]:
                self.paddle1.move(-1, dt)
            if keys[pygame.K_s]:
                self.paddle1.move(1, dt)
            
            # Player 2 (Up/Down)
            if keys[pygame.K_UP]:
                self.paddle2.move(-1, dt)
            if keys[pygame.K_DOWN]:
                self.paddle2.move(1, dt)

    def check_collisions(self):
        # Top/Bottom Wall Collisions
        if self.ball.rect.top <= 0:
            self.ball.rect.top = 0
            self.ball.y_float = float(self.ball.rect.y)
            self.ball.vy = abs(self.ball.vy) # Force down
        elif self.ball.rect.bottom >= SCREEN_HEIGHT:
            self.ball.rect.bottom = SCREEN_HEIGHT
            self.ball.y_float = float(self.ball.rect.y)
            self.ball.vy = -abs(self.ball.vy) # Force up

        # Left/Right Wall Collisions (Goals)
        if self.ball.rect.right < 0:
            self.score2 += 1
            self.goal_scored(-1) # Serve to player 1
        elif self.ball.rect.left > SCREEN_WIDTH:
            self.score1 += 1
            self.goal_scored(1) # Serve to player 2

        # Paddle Collisions
        if self.ball.vx < 0 and self.ball.rect.colliderect(self.paddle1.rect):
            self.handle_paddle_collision(self.paddle1, 1)
        elif self.ball.vx > 0 and self.ball.rect.colliderect(self.paddle2.rect):
            self.handle_paddle_collision(self.paddle2, -1)

    def handle_paddle_collision(self, paddle, direction_x):
        # Increase speed
        self.ball.speed *= BALL_SPEED_MULTIPLIER
        
        # Calculate dynamic bounce angle
        # Relative intersect Y from center of paddle
        relative_intersect_y = (paddle.rect.y + (paddle.rect.height / 2)) - self.ball.rect.centery
        # Normalize relative intersection from -1 to 1
        normalized_relative_intersection_y = (relative_intersect_y / (paddle.rect.height / 2))
        
        # Calculate bounce angle (negative because standard screen coords have Y pointing down)
        bounce_angle = normalized_relative_intersection_y * MAX_BOUNCE_ANGLE * -1
        
        # Apply new velocity based on angle and new speed
        self.ball.vx = self.ball.speed * math.cos(bounce_angle) * direction_x
        self.ball.vy = self.ball.speed * math.sin(bounce_angle)
        
        # Nudge ball out of paddle to prevent sticking
        if direction_x == 1:
            self.ball.rect.left = paddle.rect.right
        else:
            self.ball.rect.right = paddle.rect.left
        self.ball.x_float = float(self.ball.rect.x)

    def goal_scored(self, serve_direction):
        if self.score1 >= MAX_SCORE:
            self.winner_text = "Player 1 Wins!"
            self.state = STATE_GAME_OVER
        elif self.score2 >= MAX_SCORE:
            self.winner_text = "Player 2 Wins!"
            self.state = STATE_GAME_OVER
        else:
            self.state = STATE_SERVE
            self.serve_timer = 1.0
            self.serve_direction = serve_direction
            self.ball.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, dt):
        if self.state == STATE_SERVE:
            self.serve_timer -= dt
            if self.serve_timer <= 0:
                self.state = STATE_PLAYING
                self.ball.serve(self.serve_direction)
                
        elif self.state == STATE_PLAYING:
            self.ball.update(dt)
            self.check_collisions()

    def draw_dashed_line(self, surface, color, start_pos, end_pos, width=1, dash_length=10):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dl = dash_length

        if (x1 == x2):
            ycoords = [y for y in range(y1, y2, dl if y1 < y2 else -dl)]
            xcoords = [x1] * len(ycoords)
        elif (y1 == y2):
            xcoords = [x for x in range(x1, x2, dl if x1 < x2 else -dl)]
            ycoords = [y1] * len(xcoords)
        else:
            a = abs(x2 - x1)
            b = abs(y2 - y1)
            c = round(math.sqrt(a**2 + b**2))
            dx = dl * a / c
            dy = dl * b / c

            xcoords = [x for x in range(x1, x2, round(dx) if x1 < x2 else -round(dx))]
            ycoords = [y for y in range(y1, y2, round(dy) if y1 < y2 else -round(dy))]

        next_coords = list(zip(xcoords[1::2], ycoords[1::2]))
        last_coords = list(zip(xcoords[0::2], ycoords[0::2]))
        for (x1, y1), (x2, y2) in zip(next_coords, last_coords):
            start = (round(x1), round(y1))
            end = (round(x2), round(y2))
            pygame.draw.line(surface, color, start, end, width)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw Net
        self.draw_dashed_line(self.screen, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), width=2, dash_length=15)
        
        # Draw Score
        score_text = self.font.render(f"{self.score1}    {self.score2}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(score_text, score_rect)
        
        # Draw Entities
        self.paddle1.draw(self.screen)
        self.paddle2.draw(self.screen)
        if self.state in [STATE_PLAYING, STATE_SERVE]:
            self.ball.draw(self.screen)
            
        # UI overlays
        if self.state == STATE_MENU:
            title_text = self.large_font.render("PONG KOMBAT", True, WHITE)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            start_text = self.font.render("Press SPACE to Start", True, WHITE)
            start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(start_text, start_rect)
            
        elif self.state == STATE_GAME_OVER:
            win_text = self.large_font.render(self.winner_text, True, WHITE)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            restart_text = self.font.render("Press SPACE to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            self.screen.blit(win_text, win_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0 # Delta time in seconds
            self.handle_input(dt)
            self.update(dt)
            self.draw()

if __name__ == "__main__":
    game = Game()
    game.run()
