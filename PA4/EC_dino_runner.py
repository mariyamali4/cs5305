import pygame
import random
import sys
import os

pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DINO_COLOR = (83, 83, 83)
OBSTACLE_COLOR = (34, 139, 34)
PTRO_COLOR = (120, 120, 120)
GROUND_COLOR = (50, 50, 50)
BG_COLOR = (235, 235, 235)

FONT_NAME = pygame.font.get_default_font()
HIGH_SCORE_FILE = "highscore.txt"

class Dino:
    def __init__(self):
        self.width = 44
        self.height = 47
        self.duck_width = 59
        self.duck_height = 30
        self.x = 50
        self.y = GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.gravity = 1
        self.jump_strength = 18
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = -self.jump_strength
            self.is_jumping = True

    def duck(self, ducking):
        if self.is_jumping:
            return  # Can't duck while jumping
        if ducking and not self.is_ducking:
            self.is_ducking = True
            self.rect.width = self.duck_width
            self.rect.height = self.duck_height
            self.y = GROUND_HEIGHT - self.duck_height
            self.rect.topleft = (self.x, self.y)
        elif not ducking and self.is_ducking:
            self.is_ducking = False
            self.rect.width = self.width
            self.rect.height = self.height
            self.y = GROUND_HEIGHT - self.height
            self.rect.topleft = (self.x, self.y)

    def update(self):
        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y += self.velocity_y
            if self.y >= GROUND_HEIGHT - (self.duck_height if self.is_ducking else self.height):
                self.y = GROUND_HEIGHT - (self.duck_height if self.is_ducking else self.height)
                self.is_jumping = False
                self.velocity_y = 0
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        if self.is_ducking:
            dino_rect = pygame.Rect(self.x, self.y, self.duck_width, self.duck_height)
            pygame.draw.rect(screen, DINO_COLOR, dino_rect)
            # Draw eye
            eye_rect = pygame.Rect(self.x + 45, self.y + 8, 6, 6)
            pygame.draw.rect(screen, BLACK, eye_rect)
            # Draw legs (simple rectangles)
            leg1 = pygame.Rect(self.x + 10, self.y + self.duck_height - 10, 15, 10)
            leg2 = pygame.Rect(self.x + 35, self.y + self.duck_height - 10, 15, 10)
            pygame.draw.rect(screen, DINO_COLOR, leg1)
            pygame.draw.rect(screen, DINO_COLOR, leg2)
        else:
            # Draw body
            pygame.draw.rect(screen, DINO_COLOR, self.rect)
            # Draw eye
            eye_rect = pygame.Rect(self.x + 30, self.y + 10, 6, 6)
            pygame.draw.rect(screen, BLACK, eye_rect)
            # Draw legs (simple rectangles)
            leg1 = pygame.Rect(self.x + 10, self.y + self.height - 10, 10, 10)
            leg2 = pygame.Rect(self.x + 25, self.y + self.height - 10, 10, 10)
            pygame.draw.rect(screen, DINO_COLOR, leg1)
            pygame.draw.rect(screen, DINO_COLOR, leg2)

class Obstacle:
    spike_height = 10

    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.image = pygame.Surface((self.width, self.height + self.spike_height), pygame.SRCALPHA)
        self._draw_obstacle_image()

    def _draw_obstacle_image(self):
        self.image.fill((0, 0, 0, 0))  # Transparent
        pygame.draw.rect(self.image, OBSTACLE_COLOR, (0, self.spike_height, self.width, self.height))
        spike_width = 6
        for i in range(0, self.width, spike_width * 2):
            spike = [
                (i, self.spike_height),
                (i + spike_width, 0),
                (i + spike_width * 2, self.spike_height)
            ]
            pygame.draw.polygon(self.image, OBSTACLE_COLOR, spike)

    def update(self):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y - self.spike_height))

    def off_screen(self):
        return self.x + self.width < 0

class Pterodactyl:
    def __init__(self, x, y, speed):
        self.width = 46
        self.height = 40
        self.x = x
        self.y = y
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_interval = 200  # milliseconds
        self.last_update = pygame.time.get_ticks()
        self._create_images()

    def _create_images(self):
        # Create two simple wing positions for flapping animation
        surf1 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf2 = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Frame 1: wings up
        pygame.draw.polygon(surf1, PTRO_COLOR, [(0, self.height), (self.width//2, 0), (self.width, self.height)])
        pygame.draw.rect(surf1, PTRO_COLOR, (self.width//4, self.height//2, self.width//2, self.height//2))

        # Frame 2: wings down
        pygame.draw.polygon(surf2, PTRO_COLOR, [(0, 0), (self.width//2, self.height), (self.width, 0)])
        pygame.draw.rect(surf2, PTRO_COLOR, (self.width//4, 0, self.width//2, self.height//2))

        self.animation_frames = [surf1, surf2]

    def update(self):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)
        now = pygame.time.get_ticks()
        self.animation_timer += now - self.last_update
        self.last_update = now
        if self.animation_timer > self.animation_interval:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.animation_timer = 0

    def draw(self, screen):
        screen.blit(self.animation_frames[self.current_frame], (self.x, self.y))

    def off_screen(self):
        return self.x + self.width < 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chrome Dino Runner")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(FONT_NAME, 24)
        self.big_font = pygame.font.Font(FONT_NAME, 48)
        self.reset()
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def reset(self):
        self.dino = Dino()
        self.obstacles = []
        self.pterodactyls = []
        self.score = 0
        self.game_speed = 10
        self.spawn_timer = 0
        self.spawn_interval = 1500  # milliseconds
        self.running = True
        self.game_over = False
        self.start_screen = True
        self.last_spawn_time = pygame.time.get_ticks()
        self.last_score_update = pygame.time.get_ticks()
        self.ducking = False
        self.last_speed_increase_score = 0
        self.last_obstacle_spawn_x = SCREEN_WIDTH  # Track last obstacle x to space obstacles

    def spawn_obstacle(self):
        # Ensure spacing between obstacles
        min_spacing = 150
        if self.obstacles:
            last_obstacle = self.obstacles[-1]
            if last_obstacle.x > SCREEN_WIDTH - min_spacing:
                return
        if self.pterodactyls:
            last_ptero = self.pterodactyls[-1]
            if last_ptero.x > SCREEN_WIDTH - min_spacing:
                return

        # Randomly spawn cactus or pterodactyl
        obstacle_type = random.choices(['cactus', 'pterodactyl'], weights=[70, 30])[0]
        if obstacle_type == 'cactus':
            width = random.choice([20, 25, 30])
            height = random.choice([40, 45, 50])
            x = SCREEN_WIDTH + 20
            y = GROUND_HEIGHT - height
            obstacle = Obstacle(x, y, width, height, self.game_speed)
            self.obstacles.append(obstacle)
        else:
            x = SCREEN_WIDTH + 20
            # Flying heights: low, mid, high
            y = random.choice([GROUND_HEIGHT - 120, GROUND_HEIGHT - 150, GROUND_HEIGHT - 180])
            ptero = Pterodactyl(x, y, self.game_speed)
            self.pterodactyls.append(ptero)

    def handle_events(self):
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.start_screen:
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.dino.duck(True)
                self.ducking = True
            else:
                if self.ducking:
                    self.dino.duck(False)
                    self.ducking = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.save_high_score()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.save_high_score()
                    pygame.quit()
                    sys.exit()
                if not self.game_over and not self.start_screen:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.dino.jump()
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset()
                if self.start_screen:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.start_screen = False

    def update(self):
        if self.start_screen or self.game_over:
            return

        self.dino.update()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_obstacle()
            self.last_spawn_time = current_time
            # Decrease spawn interval to increase difficulty, min 700ms
            if self.spawn_interval > 700:
                self.spawn_interval -= 15

        for obstacle in self.obstacles:
            obstacle.speed = self.game_speed
            obstacle.update()
        self.obstacles = [ob for ob in self.obstacles if not ob.off_screen()]

        for ptero in self.pterodactyls:
            ptero.speed = self.game_speed
            ptero.update()
        self.pterodactyls = [p for p in self.pterodactyls if not p.off_screen()]

        self.check_collisions()

        # Increase score based on time elapsed for consistency
        elapsed = current_time - self.last_score_update
        if elapsed > 50:  # update score every ~50ms
            self.score += int(elapsed / 50)
            self.last_score_update = current_time

        # Increase game speed every 100 points, max 25, only once per threshold
        if (self.score // 100) > self.last_speed_increase_score and self.game_speed < 25:
            self.game_speed += 0.5
            self.last_speed_increase_score = self.score // 100

    def check_collisions(self):
        for obstacle in self.obstacles:
            if self.dino.rect.colliderect(obstacle.rect):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return
        for ptero in self.pterodactyls:
            if self.dino.rect.colliderect(ptero.rect):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return

    def draw_ground(self):
        pygame.draw.line(self.screen, GROUND_COLOR, (0, GROUND_HEIGHT), (SCREEN_WIDTH, GROUND_HEIGHT), 3)

    def draw_score(self):
        score_surf = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 20, 20))
        high_score_surf = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(high_score_surf, (20, 20))

    def draw_start_screen(self):
        self.screen.fill(BG_COLOR)
        title_surf = self.big_font.render("Chrome Dino Runner", True, BLACK)
        instr_surf = self.font.render("Press SPACE or UP to start", True, BLACK)
        high_score_surf = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(title_surf, ((SCREEN_WIDTH - title_surf.get_width()) // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(instr_surf, ((SCREEN_WIDTH - instr_surf.get_width()) // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(high_score_surf, ((SCREEN_WIDTH - high_score_surf.get_width()) // 2, SCREEN_HEIGHT // 2 + 40))
        self.draw_ground()
        self.dino.draw(self.screen)
        pygame.display.flip()

    def draw_game_over(self):
        self.screen.fill(BG_COLOR)
        over_surf = self.big_font.render("Game Over", True, BLACK)
        score_surf = self.font.render(f"Final Score: {self.score}", True, BLACK)
        high_score_surf = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        instr_surf = self.font.render("Press R to Restart or ESC to Quit", True, BLACK)
        self.screen.blit(over_surf, ((SCREEN_WIDTH - over_surf.get_width()) // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(score_surf, ((SCREEN_WIDTH - score_surf.get_width()) // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(high_score_surf, ((SCREEN_WIDTH - high_score_surf.get_width()) // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(instr_surf, ((SCREEN_WIDTH - instr_surf.get_width()) // 2, SCREEN_HEIGHT // 2 + 70))
        self.draw_ground()
        self.dino.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for ptero in self.pterodactyls:
            ptero.draw(self.screen)
        pygame.display.flip()

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_ground()
        self.dino.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for ptero in self.pterodactyls:
            ptero.draw(self.screen)
        self.draw_score()
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            if self.start_screen:
                self.draw_start_screen()
            elif self.game_over:
                self.draw_game_over()
            else:
                self.update()
                self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()