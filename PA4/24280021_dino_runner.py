import pygame
import random
import sys
import os
import json

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DINO_COLOR = (83, 83, 83)
DINO_DUCK_COLOR = (60, 60, 60)
CACTUS_COLOR = (34, 139, 34)
BIRD_COLOR = (200, 50, 50)
GROUND_COLOR = (83, 83, 83)

FONT_NAME = pygame.font.get_default_font()
HIGH_SCORE_FILE = "high_score.json"

# Sound initialization with fallback if no mixer available
try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except Exception:
    SOUND_ENABLED = False

def load_sound(path):
    if SOUND_ENABLED and os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

# Simple beep sounds for jump, duck, collision, score
JUMP_SOUND = load_sound("jump.wav")
DUCK_SOUND = load_sound("duck.wav")
COLLISION_SOUND = load_sound("collision.wav")
SCORE_SOUND = load_sound("score.wav")

class Dino:
    WIDTH = 44
    HEIGHT = 47
    DUCK_HEIGHT = 25
    JUMP_VELOCITY = -15
    GRAVITY = 1.0
    TERMINAL_VELOCITY = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        self.step_index = 0  # For simple animation

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = self.JUMP_VELOCITY
            self.is_jumping = True
            if JUMP_SOUND:
                JUMP_SOUND.play()

    def duck(self, ducking):
        if not self.is_jumping:
            if ducking and not self.is_ducking:
                self.is_ducking = True
                self.rect.height = self.DUCK_HEIGHT
                self.y = GROUND_HEIGHT - self.DUCK_HEIGHT
                self.rect.y = self.y
                if DUCK_SOUND:
                    DUCK_SOUND.play()
            elif not ducking and self.is_ducking:
                self.is_ducking = False
                self.y = self.base_y
                self.rect.height = self.HEIGHT
                self.rect.y = self.y
                self.base_y = self.y  # Fix vertical position after ducking

    def update(self):
        if self.is_jumping:
            self.velocity_y += self.GRAVITY
            if self.velocity_y > self.TERMINAL_VELOCITY:
                self.velocity_y = self.TERMINAL_VELOCITY
            self.y += self.velocity_y
            if self.y >= self.base_y:
                self.y = self.base_y
                self.is_jumping = False
                self.velocity_y = 0
        # Update rect height and y respecting ducking state to avoid flicker
        if self.is_ducking:
            self.rect.height = self.DUCK_HEIGHT
            self.rect.y = self.y
        else:
            self.rect.height = self.HEIGHT
            self.rect.y = self.y
        self.rect.x = self.x
        self.rect.topleft = (self.rect.x, self.rect.y)

    def draw(self, surface):
        # Simple animation: alternate between two rectangles to simulate running
        if self.is_jumping:
            pygame.draw.rect(surface, DINO_COLOR, self.rect)
        else:
            if self.is_ducking:
                # Ducking pose
                pygame.draw.rect(surface, DINO_DUCK_COLOR, self.rect)
            else:
                if (self.step_index // 10) % 2 == 0:
                    # Standing pose
                    pygame.draw.rect(surface, DINO_COLOR, self.rect)
                else:
                    # Slightly different pose (simulate running)
                    rect2 = pygame.Rect(self.x, self.y + 5, self.WIDTH, self.HEIGHT - 5)
                    pygame.draw.rect(surface, DINO_COLOR, rect2)
                self.step_index = (self.step_index + 1) % 20

class Obstacle:
    def __init__(self, x, y, speed, type_):
        self.x = x
        self.base_y = y
        self.speed = speed
        self.type = type_
        if self.type == "cactus":
            self.width = 20
            self.height = 40
            self.color = CACTUS_COLOR
        elif self.type == "bird":
            self.width = 34
            self.height = 24
            self.color = BIRD_COLOR
            self.bird_fly_index = 0
            self.bird_fly_height_variation = [0, -7, 0, 7]
        else:
            self.width = 20
            self.height = 40
            self.color = CACTUS_COLOR
        self.rect = pygame.Rect(self.x, self.base_y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        if self.type == "bird":
            # Simple up/down flying animation relative to base_y
            self.bird_fly_index = (self.bird_fly_index + 1) % len(self.bird_fly_height_variation)
            self.rect.y = self.base_y + self.bird_fly_height_variation[self.bird_fly_index]
        else:
            self.rect.y = self.base_y
        self.rect.x = self.x

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def off_screen(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chrome Dino Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 20)
        self.big_font = pygame.font.Font(FONT_NAME, 40)
        self.load_high_score()
        self.reset()
        self.paused = False
        self.show_start_screen = True
        self.start_screen_duration = 3000  # milliseconds
        self.start_screen_start_time = pygame.time.get_ticks()

    def load_high_score(self):
        self.high_score = 0
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                    self.high_score = data.get("high_score", 0)
            except Exception:
                self.high_score = 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except Exception:
            pass

    def reset(self):
        self.dino = Dino(50, GROUND_HEIGHT - Dino.HEIGHT)
        self.obstacles = []
        self.score = 0
        self.game_speed = 7
        self.spawn_interval = 1500  # milliseconds
        self.last_spawn_time = pygame.time.get_ticks()
        self.game_over = False
        self.score_timer = 0
        self.score_increment_interval = 100  # milliseconds
        self.paused = False
        self.show_start_screen = False

    def spawn_obstacle(self):
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time > self.spawn_interval:
            self.last_spawn_time = now
            obstacle_type = random.choices(
                ["cactus", "bird"],
                weights=[80, 20],
                k=1
            )[0]
            if obstacle_type == "cactus":
                y = GROUND_HEIGHT - 40
            else:  # bird
                # Clamp bird base_y between 150 and 250 to avoid clipping
                y = random.randint(150, 250)
            obstacle = Obstacle(SCREEN_WIDTH + 20, y, self.game_speed, obstacle_type)
            self.obstacles.append(obstacle)
            # Decrease spawn interval to increase difficulty but keep a minimum
            self.spawn_interval = max(700, self.spawn_interval - 3)

    def check_collisions(self):
        for obstacle in self.obstacles:
            if self.dino.rect.colliderect(obstacle.rect):
                self.game_over = True
                if COLLISION_SOUND:
                    COLLISION_SOUND.play()
                break

    def update_score(self, dt):
        self.score_timer += dt
        while self.score_timer >= self.score_increment_interval:
            self.score += 1
            self.score_timer -= self.score_increment_interval
            if self.score % 100 == 0:
                self.game_speed = min(self.game_speed + 0.5, 20)
                if SCORE_SOUND:
                    SCORE_SOUND.play()

    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(high_score_text, (SCREEN_WIDTH - 350, 20))

    def draw_ground(self):
        pygame.draw.line(self.screen, GROUND_COLOR, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 3)

    def game_over_screen(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        self.screen.fill(WHITE)
        game_over_text = self.big_font.render("GAME OVER", True, BLACK)
        score_text = self.font.render(f"Your Score: {self.score}", True, BLACK)
        high_score_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        restart_text = self.font.render("Press R or Enter to Restart, ESC to Quit", True, BLACK)
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 100))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 180))
        self.screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, 210))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, 260))
        pygame.display.update()

    def pause_screen(self):
        self.screen.fill(WHITE)
        pause_text = self.big_font.render("PAUSED", True, BLACK)
        resume_text = self.font.render("Press P to Resume", True, BLACK)
        self.screen.blit(pause_text, (SCREEN_WIDTH//2 - pause_text.get_width()//2, 150))
        self.screen.blit(resume_text, (SCREEN_WIDTH//2 - resume_text.get_width()//2, 210))
        pygame.display.update()

    def start_screen(self):
        self.screen.fill(WHITE)
        title_text = self.big_font.render("Chrome Dino Runner", True, BLACK)
        instructions = [
            "Press SPACE or UP to Jump",
            "Press DOWN or CTRL to Duck",
            "Press P to Pause/Resume",
            "Avoid obstacles and survive as long as possible!",
            "Press any key to start"
        ]
        self.screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 80))
        for i, line in enumerate(instructions):
            instr_text = self.font.render(line, True, BLACK)
            self.screen.blit(instr_text, (SCREEN_WIDTH//2 - instr_text.get_width()//2, 160 + i*30))
        pygame.display.update()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.show_start_screen:
                        self.show_start_screen = False
                    elif not self.game_over and not self.paused:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                            self.dino.jump()
                        if event.key == pygame.K_DOWN or event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                            self.dino.duck(True)
                        if event.key == pygame.K_p:
                            self.paused = True
                    elif self.paused:
                        if event.key == pygame.K_p:
                            self.paused = False
                    if self.game_over:
                        if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                            self.reset()
                        if event.key == pygame.K_ESCAPE:
                            running = False
                    if event.key == pygame.K_ESCAPE:
                        running = False
                if event.type == pygame.KEYUP:
                    if not self.game_over and not self.paused:
                        if event.key == pygame.K_DOWN or event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                            self.dino.duck(False)

            if self.show_start_screen:
                self.start_screen()
                continue

            if not self.game_over and not self.paused:
                self.screen.fill(WHITE)
                self.draw_ground()

                self.spawn_obstacle()

                self.dino.update()
                self.dino.draw(self.screen)

                # Remove only obstacles that are off-screen
                self.obstacles = [ob for ob in self.obstacles if not ob.off_screen()]

                for obstacle in self.obstacles:
                    obstacle.update()
                    obstacle.draw(self.screen)

                self.check_collisions()
                self.update_score(dt)
                self.draw_score()

                pygame.display.update()

            elif self.game_over:
                self.game_over_screen()

            elif self.paused:
                self.pause_screen()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()