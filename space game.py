import pygame
import sys
import random
import sqlite3

pygame.font.init()
pygame.mixer.init()
background_music = pygame.mixer.Sound('music/space_line.mp3')
shooting_sound = pygame.mixer.Sound('music/shoot.mp3')

background_music.play(-1)  # -1 for looping
shooting_sound.set_volume(0.25)

# variable
WIDTH, HEIGHT = 900, 560
player_size = 50
enemy_size = 50
laser_size = 10

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("space X : space war")
mainfont = pygame.font.SysFont("comicSans", 30)
lost_font = pygame.font.SysFont("comicSans", 45)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

player_img = pygame.image.load('pictures/yellow1.png')
enemy_img = pygame.image.load('pictures/enemi_ship.png')
boos_img = pygame.image.load('pictures/boos_ship.png')
player_laser_img = pygame.image.load('pictures/green_lazer.png')
enemy_laser_img = pygame.image.load('pictures/red_lazer.png')
BG = pygame.image.load('pictures/space.jpg')


def collision(obj1, obj2):
    X = obj2.x - obj1.x
    Y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (X, Y)) is not None


def draw_lost():
    font = pygame.font.Font(None, 40)
    info_text = font.render(f"You lose", True, WHITE)
    window.blit(info_text, (WIDTH / 2 - 20, HEIGHT / 2))


def display_info(player_name):
    font = pygame.font.Font(None, 25)
    info_text = font.render(f"Player: {player_name}", True, WHITE)
    window.blit(info_text, (10, 10))


def display_level(level):
    font = pygame.font.Font(None, 25)
    info_text = font.render(f"Level: {level}", True, WHITE)
    window.blit(info_text, (10, 30))


def display_score(score):
    font = pygame.font.Font(None, 25)
    info_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(info_text, (10, 50))


# ship class
class Ship:
    Frame_between_shot = 30  # 30 frame = 5 sec

    def __init__(self, x, y, health):
        self.x = x
        self.y = y
        self.health = health
        self.ship = None
        self.laser = None
        self.lasers = []
        self.frame_counter = 0

    def move_laser(self, speed, obj):
        self.frame_counter -= 1
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision_laser(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def shoot(self):
        if self.frame_counter <= 0:
            laser = Laser(self.x, self.y, self.laser)
            self.lasers.append(laser)
            self.frame_counter = self.Frame_between_shot
        else:
            self.frame_counter -= 1

    def draw(self, window):
        window.blit(self.ship, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, speed):
        self.y += speed

    def off_screen(self, height):
        return self.y > height or self.y < 0

    def collision_laser(self, obj):
        return collision(self, obj)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))


# Player and enemy ship
class Player(Ship):
    def __init__(self, ship, x, y, health=100):
        super().__init__(x, y, health)
        self.ship = ship
        self.laser = player_laser_img
        self.mask = pygame.mask.from_surface(self.ship)
        self.max_health = health

    def move_laser(self, speed, objs, score):
        self.frame_counter -= 1
        for laser in self.lasers:
            laser.move(speed)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision_laser(obj):
                        objs.remove(obj)
                        score += 10
                        return score
        return score

    def shoot(self):
        if self.frame_counter <= 0:
            laser = Laser(self.x + 25, self.y, self.laser)
            self.lasers.append(laser)
            self.frame_counter = self.Frame_between_shot
        else:
            self.frame_counter -= 1

    def draw(self, window):
        super().draw(window)
        self.draw_healthbar(window)

    def draw_healthbar(self, window):
        pygame.draw.rect(window, RED, (860, 10, self.ship.get_width(), 10))
        pygame.draw.rect(window, GREEN, (860, 10, self.ship.get_width() * (self.health / self.max_health), 10))


class Enemy(Ship):
    Enemy_MAP = {
        '0': (boos_img, enemy_laser_img),
        '1': (enemy_img, enemy_laser_img),
        '2': (pygame.image.load('pictures/red1.png'), enemy_laser_img),
        '3': (pygame.image.load('pictures/red2.png'), enemy_laser_img),
        '4': (pygame.image.load('pictures/blue1.png'), enemy_laser_img),
        '5': (pygame.image.load('pictures/blue2.png'), enemy_laser_img),
        '6': (pygame.image.load('pictures/blue3.png'), enemy_laser_img),
        '7': (pygame.image.load('pictures/blue4.png'), enemy_laser_img),
        '8': (pygame.image.load('pictures/blue5.png'), enemy_laser_img),
        '9': (pygame.image.load('pictures/player_ship.png'), enemy_laser_img),
        '10': (pygame.image.load('pictures/red3.png'), enemy_laser_img),
        '11': (pygame.image.load('pictures/white1.png'), enemy_laser_img),
        '12': (pygame.image.load('pictures/red5.png'), enemy_laser_img),
        '13': (pygame.image.load('pictures/white2.png'), enemy_laser_img),
        '14': (pygame.image.load('pictures/black1.png'), enemy_laser_img),
    }

    def __init__(self, x, y, Type, health=100):
        super().__init__(x, y, health)
        self.ship, self.laser = self.Enemy_MAP[Type]
        self.mask = pygame.mask.from_surface(self.ship)

    def move(self, speed):
        self.y += speed

    def shoot(self):
        if self.frame_counter <= 0:
            laser = Laser(self.x + 18, self.y + 100, self.laser)
            self.lasers.append(laser)
            self.frame_counter = self.Frame_between_shot
        else:
            self.frame_counter -= 1


def get_player_name(clock, FPS):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width

        window.blit(BG, (0, 0))
        pygame.draw.rect(window, color, input_box, 2)
        window.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()
        clock.tick(FPS)


def game_over():
    font = pygame.font.Font(None, 50)
    window.fill(BLACK)
    game_over_text = font.render("Game Over!", True, WHITE)
    replay_text = font.render("Play again? Y/N", True, WHITE)
    window.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 30))
    window.blit(replay_text, (WIDTH // 2 - 130, HEIGHT // 2 + 20))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                elif event.key == pygame.K_n:
                    return False


def main():
    FPS = 60
    level = 0

    enemies = []
    wave_nbr = 5
    enemies_speed = 1
    player_speed = 5
    laser_speed = 5
    score = 0
    player = Player(player_img, 450, 545)
    lost = False
    lost_count = 0
    clock = pygame.time.Clock()
    run = True
    player_name = get_player_name(clock, FPS)

    def redraw_window():
        window.blit(BG, (0, 0))
        display_info(player_name)
        display_level(level)
        display_score(score)
        for enemy in enemies:
            enemy.draw(window)
        player.draw(window)
        if lost:
            draw_lost()
        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()
        if player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            enemies_speed += 0.25
            wave_nbr = 3 + round(level / 2)
            for _ in range(wave_nbr):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1300, -100),
                              random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13']))
                enemies.append(enemy)
            for _ in range(round(level / 2)):
                if level >= 5:
                    enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1300, -100), random.choice(['0', '14']))
                    enemies.append(enemy)

        # Movement player
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and player.x - player_speed > 0:
            player.x -= player_speed

        if keys[pygame.K_RIGHT] and player.x + player_speed < HEIGHT + 220:
            player.x += player_speed

        if keys[pygame.K_UP] and player.y - player_speed > 0:
            player.y -= player_speed

        if keys[pygame.K_DOWN] and player.y + player_speed < HEIGHT - player_size:
            player.y += player_speed

        # Shooting player lasers
        if keys[pygame.K_SPACE]:
            player.shoot()
            shooting_sound.play()

        for enemy in enemies[:]:
            enemy.move(enemies_speed)
            enemy.move_laser(laser_speed, player)
            if random.randrange(0, 120) == 1:
                enemy.shoot()
            if collision(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y > HEIGHT:
                enemies.remove(enemy)

        player.move_laser(-laser_speed, enemies, score)
        score = player.move_laser(-laser_speed, enemies, score)
        display_score(score)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def main_menu():
    running = True
    font = pygame.font.Font(None, 25)
    loading_bar = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 0, 10)
    loading_progress = 0

    story_text = [
        "Welcome to Space X",
        "you are our last hope",
        "Evil alien forces are invading",
        "Instructions:",
        "- Use arrow keys to move your ship",
        "- Press SPACE to shoot lasers",
        "- Survive as long as you can!",
        "",
        "Are you ready ?",
        "Click to start"
    ]

    story_font = pygame.font.Font(None, 40)

    for text in story_text:
        text_surface = story_font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.delay(2000)
        window.fill(BLACK)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                main()

        pygame.draw.rect(window, WHITE, loading_bar)
        pygame.draw.rect(window, GREEN, (loading_bar.x, loading_bar.y, loading_progress, 10))
        pygame.display.flip()

        if loading_progress < 200:
            loading_progress += 0.5

    pygame.quit()


main_menu()
