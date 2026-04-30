import pygame
import random
import sys
import os
import shelve

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GROUND_HEIGHT = 350
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DINO_COLOR = (83, 83, 83)
OBSTACLE_COLOR = (34, 139, 34)
PTERO_COLOR = (100, 100, 100)
GROUND_COLOR = (83, 83, 83)
TEXT_COLOR = (83, 83, 83)
GAME_OVER_COLOR = (200, 0, 0)

# Game States
START = 0
PLAYING = 1
GAME_OVER = 2

# Paths
HIGH_SCORE_FILE = "dino_highscore.db"

# Load sounds (optional, fallback to None if not found)
def load_sound(path):
    if os.path.isfile(path):
        return pygame.mixer.Sound(path)
    return None

JUMP_SOUND = load_sound("jump.wav")
DUCK_SOUND = load_sound("duck.wav")
HIT_SOUND = load_sound("hit.wav")
MILESTONE_SOUND = load_sound("milestone.wav")

class Dinosaur:
    WIDTH = 44
    HEIGHT = 47
    DUCK_WIDTH = 59
    DUCK_HEIGHT = 30
    GRAVITY = 1
    JUMP_STRENGTH = 18

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_ducking = False
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        # Animation frames: simulate running by toggling leg positions
        self.run_images = [self.create_dino_surface(leg_pos=0), self.create_dino_surface(leg_pos=1)]
        self.duck_images = [self.create_dino_surface(duck=True, leg_pos=0), self.create_dino_surface(duck=True, leg_pos=1)]
        self.jump_image = self.create_dino_surface(leg_pos=0)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # ms per frame

    def create_dino_surface(self, leg_pos=0, duck=False):
        if duck:
            surf = pygame.Surface((self.DUCK_WIDTH, self.DUCK_HEIGHT), pygame.SRCALPHA)
            # Body
            pygame.draw.rect(surf, DINO_COLOR, (10, 5, 39, 20), border_radius=6)
            # Head
            pygame.draw.rect(surf, DINO_COLOR, (0, 0, 20, 20), border_radius=6)
            # Legs (simulate running)
            if leg_pos == 0:
                pygame.draw.rect(surf, DINO_COLOR, (10, 22, 15, 7), border_radius=3)
                pygame.draw.rect(surf, DINO_COLOR, (34, 22, 15, 7), border_radius=3)
            else:
                pygame.draw.rect(surf, DINO_COLOR, (10, 25, 15, 4), border_radius=3)
                pygame.draw.rect(surf, DINO_COLOR, (34, 19, 15, 10), border_radius=3)
            return surf
        else:
            surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            # Body
            pygame.draw.rect(surf, DINO_COLOR, (10, 10, 24, 30), border_radius=6)
            # Head
            pygame.draw.rect(surf, DINO_COLOR, (0, 0, 20, 20), border_radius=6)
            # Legs (simulate running)
            if leg_pos == 0:
                pygame.draw.rect(surf, DINO_COLOR, (10, 40, 10, 7), border_radius=3)
                pygame.draw.rect(surf, DINO_COLOR, (24, 40, 10, 7), border_radius=3)
            else:
                pygame.draw.rect(surf, DINO_COLOR, (10, 43, 10, 4), border_radius=3)
                pygame.draw.rect(surf, DINO_COLOR, (24, 37, 10, 10), border_radius=3)
            return surf

    def jump(self):
        if not self.is_jumping and not self.is_ducking:
            self.velocity_y = -self.JUMP_STRENGTH
            self.is_jumping = True
            if JUMP_SOUND:
                JUMP_SOUND.play()

    def duck(self, ducking):
        if self.is_jumping:
            # Can't duck while jumping
            return
        if ducking and not self.is_ducking:
            self.is_ducking = True
            self.rect.width = self.DUCK_WIDTH
            self.rect.height = self.DUCK_HEIGHT
            self.rect.topleft = (self.x, self.base_y + (self.HEIGHT - self.DUCK_HEIGHT))
            if DUCK_SOUND:
                DUCK_SOUND.play()
        elif not ducking and self.is_ducking:
            self.is_ducking = False
            self.rect.width = self.WIDTH
            self.rect.height = self.HEIGHT
            self.rect.topleft = (self.x, self.y)

    def update(self, dt):
        if self.is_jumping:
            self.velocity_y += self.GRAVITY
            self.y += self.velocity_y
            if self.y >= self.base_y:
                self.y = self.base_y
                self.is_jumping = False
                self.velocity_y = 0
        if not self.is_ducking:
            self.rect.topleft = (self.x, self.y)
        else:
            self.rect.topleft = (self.x, self.base_y + (self.HEIGHT - self.DUCK_HEIGHT))
        # Animation update
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % 2

    def draw(self, surface):
        if self.is_jumping:
            surface.blit(self.jump_image, (self.x, self.y))
        elif self.is_ducking:
            surface.blit(self.duck_images[self.current_frame], (self.x, self.base_y + (self.HEIGHT - self.DUCK_HEIGHT)))
        else:
            surface.blit(self.run_images[self.current_frame], (self.x, self.y))


class Obstacle:
    SMALL_WIDTH = 20
    SMALL_HEIGHT = 40
    LARGE_WIDTH = 30
    LARGE_HEIGHT = 60
    COLOR = OBSTACLE_COLOR

    def __init__(self, x, ground_y, speed):
        self.x = x
        self.speed = speed
        self.type = random.choice(['small', 'large'])
        if self.type == 'small':
            self.width = self.SMALL_WIDTH
            self.height = self.SMALL_HEIGHT
        else:
            self.width = self.LARGE_WIDTH
            self.height = self.LARGE_HEIGHT
        self.y = ground_y - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        if self.type == 'small':
            pygame.draw.rect(surface, self.COLOR, (self.x + 5, self.y + 10, 10, 30), border_radius=4)
            pygame.draw.rect(surface, self.COLOR, (self.x, self.y + 20, 5, 10), border_radius=3)
            pygame.draw.rect(surface, self.COLOR, (self.x + 15, self.y + 20, 5, 10), border_radius=3)
        else:
            pygame.draw.rect(surface, self.COLOR, (self.x + 10, self.y + 10, 10, 50), border_radius=5)
            pygame.draw.rect(surface, self.COLOR, (self.x + 5, self.y + 30, 5, 20), border_radius=4)
            pygame.draw.rect(surface, self.COLOR, (self.x + 20, self.y + 30, 5, 20), border_radius=4)
            pygame.draw.rect(surface, self.COLOR, (self.x, self.y + 40, 5, 10), border_radius=3)
            pygame.draw.rect(surface, self.COLOR, (self.x + 25, self.y + 40, 5, 10), border_radius=3)

    def off_screen(self):
        return self.x + self.width < 0


class Pterodactyl:
    WIDTH = 46
    HEIGHT = 40
    COLOR = PTERO_COLOR
    FLY_HEIGHTS = [GROUND_HEIGHT - 100, GROUND_HEIGHT - 70, GROUND_HEIGHT - 50]

    def __init__(self, x, speed):
        self.x = x
        self.speed = speed
        self.y = random.choice(self.FLY_HEIGHTS)
        self.rect = pygame.Rect(self.x, self.y, self.WIDTH, self.HEIGHT)
        # Animation frames: wings up and wings down
        self.wing_up = self.create_ptero_surface(wing_up=True)
        self.wing_down = self.create_ptero_surface(wing_up=False)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame

    def create_ptero_surface(self, wing_up=True):
        surf = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(surf, self.COLOR, (10, 10, 26, 20))
        # Head
        pygame.draw.circle(surf, self.COLOR, (8, 20), 8)
        # Wings
        if wing_up:
            pygame.draw.polygon(surf, self.COLOR, [(10, 20), (0, 0), (20, 10)])
            pygame.draw.polygon(surf, self.COLOR, [(36, 20), (46, 0), (26, 10)])
        else:
            pygame.draw.polygon(surf, self.COLOR, [(10, 20), (0, 40), (20, 30)])
            pygame.draw.polygon(surf, self.COLOR, [(36, 20), (46, 40), (26, 30)])
        return surf

    def update(self, dt):
        self.x -= self.speed
        self.rect.topleft = (self.x, self.y)
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % 2

    def draw(self, surface):
        if self.current_frame == 0:
            surface.blit(self.wing_up, (self.x, self.y))
        else:
            surface.blit(self.wing_down, (self.x, self.y))

    def off_screen(self):
        return self.x + self.WIDTH < 0


class Ground:
    COLOR = GROUND_COLOR
    HEIGHT = 20

    def __init__(self, y, speed):
        self.y = y
        self.speed = speed
        self.x1 = 0
        self.x2 = SCREEN_WIDTH
        self.width = SCREEN_WIDTH

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed
        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, surface):
        pygame.draw.rect(surface, self.COLOR, (self.x1, self.y, self.width, self.HEIGHT))
        pygame.draw.rect(surface, self.COLOR, (self.x2, self.y, self.width, self.HEIGHT))


class ScoreTracker:
    COLOR = TEXT_COLOR

    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont('Arial', 24)
        self.time_accumulator = 0
        self.milestone_sound_played = False

    def update(self, dt):
        self.time_accumulator += dt
        while self.time_accumulator >= 100:
            self.score += 1
            self.time_accumulator -= 100

    def draw(self, surface):
        score_surf = self.font.render(f"Score: {self.score}", True, self.COLOR)
        surface.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 20, 20))


class HighScoreTracker:
    COLOR = TEXT_COLOR

    def __init__(self):
        self.high_score = 0
        self.font = pygame.font.SysFont('Arial', 24)
        self.load_high_score()

    def load_high_score(self):
        try:
            with shelve.open(HIGH_SCORE_FILE) as db:
                self.high_score = db.get('high_score', 0)
        except Exception:
            self.high_score = 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            try:
                with shelve.open(HIGH_SCORE_FILE) as db:
                    db['high_score'] = self.high_score
            except Exception:
                pass

    def draw(self, surface):
        high_score_surf = self.font.render(f"High Score: {self.high_score}", True, self.COLOR)
        surface.blit(high_score_surf, (20, 20))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chrome Dinosaur Runner")
        self.clock = pygame.time.Clock()
        self.game_state = START
        self.game_speed = 10
        self.spawn_timer = 0
        self.spawn_interval = random.randint(1500, 2500)  # milliseconds
        self.dinosaur = Dinosaur(50, GROUND_HEIGHT - Dinosaur.HEIGHT)
        self.ground = Ground(GROUND_HEIGHT, self.game_speed)
        self.obstacles = []
        self.pterodactyls = []
        self.score_tracker = ScoreTracker()
        self.high_score_tracker = HighScoreTracker()
        self.font_big = pygame.font.SysFont('Arial', 48)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.game_over_flash_timer = 0
        self.game_over_flash_on = True
        self.ducking = False
        self.milestone_sound_played = False

    def reset(self):
        self.game_speed = 10
        self.spawn_timer = 0
        self.spawn_interval = random.randint(1500, 2500)
        self.dinosaur = Dinosaur(50, GROUND_HEIGHT - Dinosaur.HEIGHT)
        self.ground = Ground(GROUND_HEIGHT, self.game_speed)
        self.obstacles = []
        self.pterodactyls = []
        self.score_tracker = ScoreTracker()
        self.game_state = START
        self.game_over_flash_timer = 0
        self.game_over_flash_on = True
        self.ducking = False
        self.milestone_sound_played = False

    def handle_events(self):
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.high_score_tracker.save_high_score(self.score_tracker.score)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.high_score_tracker.save_high_score(self.score_tracker.score)
                    pygame.quit()
                    sys.exit()
                if self.game_state == START:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.game_state = PLAYING
                elif self.game_state == PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.dinosaur.jump()
                    if event.key == pygame.K_DOWN or event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        self.ducking = True
                        self.dinosaur.duck(True)
                elif self.game_state == GAME_OVER:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                        self.reset()
                        self.game_state = PLAYING
            if event.type == pygame.KEYUP:
                if self.game_state == PLAYING:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        self.ducking = False
                        self.dinosaur.duck(False)
        # Also handle ducking continuously if key held down
        if self.game_state == PLAYING:
            if keys[pygame.K_DOWN] or keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if not self.ducking:
                    self.ducking = True
                    self.dinosaur.duck(True)
            else:
                if self.ducking:
                    self.ducking = False
                    self.dinosaur.duck(False)

    def spawn_obstacle_or_ptero(self):
        # 70% chance to spawn ground obstacle, 30% chance to spawn pterodactyl
        if random.random() < 0.7:
            self.obstacles.append(Obstacle(SCREEN_WIDTH + 20, GROUND_HEIGHT, self.game_speed))
        else:
            self.pterodactyls.append(Pterodactyl(SCREEN_WIDTH + 20, self.game_speed))

    def update(self, dt):
        if self.game_state == PLAYING:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.spawn_interval = random.randint(1500, 2500)
                self.spawn_obstacle_or_ptero()
            # Update game speed gradually
            self.game_speed += 0.001 * dt  # increase speed slowly
            self.ground.speed = self.game_speed
            self.ground.update()
            self.dinosaur.update(dt)
            for obstacle in self.obstacles:
                obstacle.speed = self.game_speed
                obstacle.update()
            for ptero in self.pterodactyls:
                ptero.speed = self.game_speed
                ptero.update(dt)
            # Remove off-screen obstacles and pterodactyls
            self.obstacles = [o for o in self.obstacles if not o.off_screen()]
            self.pterodactyls = [p for p in self.pterodactyls if not p.off_screen()]
            # Update score
            self.score_tracker.update(dt)
            # Play milestone sound every 100 points
            if self.score_tracker.score > 0 and self.score_tracker.score % 100 == 0:
                if not self.milestone_sound_played:
                    if MILESTONE_SOUND:
                        MILESTONE_SOUND.play()
                    self.milestone_sound_played = True
            else:
                self.milestone_sound_played = False
            # Collision detection
            for obstacle in self.obstacles:
                if self.dinosaur.rect.colliderect(obstacle.rect):
                    self.game_state = GAME_OVER
                    if HIT_SOUND:
                        HIT_SOUND.play()
                    self.high_score_tracker.save_high_score(self.score_tracker.score)
                    break
            for ptero in self.pterodactyls:
                if self.dinosaur.rect.colliderect(ptero.rect):
                    self.game_state = GAME_OVER
                    if HIT_SOUND:
                        HIT_SOUND.play()
                    self.high_score_tracker.save_high_score(self.score_tracker.score)
                    break
        elif self.game_state == GAME_OVER:
            self.game_over_flash_timer += dt
            if self.game_over_flash_timer >= 500:
                self.game_over_flash_timer = 0
                self.game_over_flash_on = not self.game_over_flash_on

    def draw(self):
        self.screen.fill(WHITE)
        self.ground.draw(self.screen)
        self.dinosaur.draw(self.screen)
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for ptero in self.pterodactyls:
            ptero.draw(self.screen)
        self.score_tracker.draw(self.screen)
        self.high_score_tracker.draw(self.screen)

        if self.game_state == START:
            title_surf = self.font_big.render("Chrome Dinosaur Runner", True, TEXT_COLOR)
            instr_surf1 = self.font_small.render("Press SPACE or UP to start and jump", True, TEXT_COLOR)
            instr_surf2 = self.font_small.render("Press DOWN or CTRL to duck", True, TEXT_COLOR)
            self.screen.blit(title_surf, ((SCREEN_WIDTH - title_surf.get_width()) // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(instr_surf1, ((SCREEN_WIDTH - instr_surf1.get_width()) // 2, SCREEN_HEIGHT // 3 + 60))
            self.screen.blit(instr_surf2, ((SCREEN_WIDTH - instr_surf2.get_width()) // 2, SCREEN_HEIGHT // 3 + 90))
        elif self.game_state == GAME_OVER:
            if self.game_over_flash_on:
                over_surf = self.font_big.render("GAME OVER", True, GAME_OVER_COLOR)
                self.screen.blit(over_surf, ((SCREEN_WIDTH - over_surf.get_width()) // 2, SCREEN_HEIGHT // 3))
            score_surf = self.font_small.render(f"Final Score: {self.score_tracker.score}", True, TEXT_COLOR)
            high_score_surf = self.font_small.render(f"High Score: {self.high_score_tracker.high_score}", True, TEXT_COLOR)
            restart_surf = self.font_small.render("Press SPACE or UP to restart", True, TEXT_COLOR)
            self.screen.blit(score_surf, ((SCREEN_WIDTH - score_surf.get_width()) // 2, SCREEN_HEIGHT // 3 + 70))
            self.screen.blit(high_score_surf, ((SCREEN_WIDTH - high_score_surf.get_width()) // 2, SCREEN_HEIGHT // 3 + 100))
            self.screen.blit(restart_surf, ((SCREEN_WIDTH - restart_surf.get_width()) // 2, SCREEN_HEIGHT // 3 + 130))

        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()