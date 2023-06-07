import os
import sys
import pygame
import pygame.image


class Player(object):
    def __init__(self, game):
        self.rect = pygame.Rect(32, 32, 16, 16)
        self.game = game
        self.has_key = False

    def move(self, dx, dy):
        if dx != 0:
            self.move_single_axis(dx, 0)
        if dy != 0:
            self.move_single_axis(0, dy)

    def move_single_axis(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

        for wall in self.game.walls:
            if self.rect.colliderect(wall.rect):
                if dx > 0:
                    self.rect.right = wall.rect.left
                if dx < 0:
                    self.rect.left = wall.rect.right
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                if dy < 0:
                    self.rect.top = wall.rect.bottom

    def collect_key(self):
        self.has_key = True

class Wall(object):
    def __init__(self, pos, game):
        game.walls.append(self)
        self.rect = pygame.Rect(pos[0], pos[1], 16, 16)


class MainMenu(object):
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.selected_option = 0
        self.options = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"]
        self.menu_rects = []

    def draw_menu(self, screen):
        title = self.font.render("Welcome to Maze Game!", True, (255, 255, 255))
        screen.blit(title, (25, 50))
        self.menu_rects = []
        for i, option in enumerate(self.options):
            text = self.font.render(option, True, (255, 255, 255))
            rect = text.get_rect(center=(175, 100 + i * 50))
            screen.blit(text, rect)
            self.menu_rects.append(rect)
        pygame.display.flip()

    def run_menu(self, screen):
        self.draw_menu(screen)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return self.selected_option
            for i, rect in enumerate(self.menu_rects):
                if i == self.selected_option:
                    pygame.draw.rect(screen, (255, 128, 0), rect, 3)
                else:
                    pygame.draw.rect(screen, (255, 255, 255), rect, 3)
            pygame.display.flip()


# Game class
class Game(object):
    def __init__(self, level):
        self.level = level
        self.walls = []
        self.player = None
        self.end_rect = None
        self.key_rect = None
        self.timer_rect = pygame.Rect(150, 0, 100, 20)
        self.exit_sprite = pygame.image.load("exit.png")
        self.key_sprite = pygame.image.load("key.png")
        self.key_sprite = pygame.transform.scale(self.key_sprite, (16, 16))
        self.key_pos = []
        self.exit_sprite = pygame.transform.scale(self.exit_sprite, (16, 16))
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        pygame.init()
        pygame.display.set_caption("Leave every hope, ye who enter!")
        self.screen = pygame.display.set_mode((336, 336))
        self.clock = pygame.time.Clock()
        self.load_level()

    def load_level(self):
        x = y = 0
        for row in self.level:
            for col in row:
                if col == "W":
                    self.walls.append(Wall((x, y), self))
                if col == "E":
                    self.end_rect = pygame.Rect(x, y, 16, 16)
                if col == "K":
                    self.key_rect = pygame.Rect(x, y, 16, 16)
                    self.key_pos = [x, y]
                x += 16
            y += 16
            x = 0

    def draw_level(self):
        self.screen.fill((0, 0, 0))
        for wall in self.walls:
            pygame.draw.rect(self.screen, (255, 255, 255), wall.rect)
        if self.key_rect is not None and not self.player.has_key:
            self.screen.blit(self.key_sprite, self.key_rect)
        if self.player.has_key:
            pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(self.key_pos[0], self.key_pos[1], 16, 16))

        self.screen.blit(self.exit_sprite, self.end_rect)
        pygame.draw.rect(self.screen, (255, 200, 0), self.player.rect)
        pygame.display.flip()
        timer_text = pygame.font.Font(None, 24).render(f"Time spent: {int(self.seconds)}", True, (0, 0, 0))
        self.screen.blit(timer_text, self.timer_rect)

    def is_collision(self, rect):
        for wall in self.walls:
            if rect.colliderect(wall.rect):
                return True
        return False

    def run_game(self):
        self.key_sprite = pygame.image.load("key.png")
        self.key_sprite = pygame.transform.scale(self.key_sprite, (16, 16))
        self.player = Player(self)
        start = pygame.time.get_ticks()
        pygame.display.flip()
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.pause_game()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()
                    quit()
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                self.player.move(-2, 0)
            if key[pygame.K_RIGHT]:
                self.player.move(2, 0)
            if key[pygame.K_UP]:
                self.player.move(0, -2)
            if key[pygame.K_DOWN]:
                self.player.move(0, 2)
            if self.player.rect.colliderect(self.end_rect):
                if self.player.has_key:
                    self.show_win_screen()
                else:
                    self.show_loss_screen()
                running = False
            if self.key_rect and self.key_sprite is not None and self.player.rect.colliderect(self.key_rect):
                self.player.collect_key()
                self.key_sprite = None
            self.seconds = (pygame.time.get_ticks() - start) / 1000
            pygame.display.flip()
            if self.seconds > 30:
                self.show_loss_screen()
                running = False
            self.draw_level()

    def pause_game(self):
        paused = True
        self.screen.fill((0, 0, 0))
        menu_rects = self.pause_menu()
        pygame.display.flip()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    elif event.key == pygame.K_ESCAPE:
                        paused = False
                        self.show_menu()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if menu_rects[0].collidepoint(pos):
                        paused = False
                    elif menu_rects[1].collidepoint(pos):
                        paused = False
                        self.show_menu()

    def show_win_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render("You won!", True, (255, 255, 255))
        rect = text.get_rect(center=(175, 120))
        self.screen.blit(text, rect)
        pygame.display.flip()
        self.show_repeat_menu()

    def show_loss_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 36)
        text = font.render("You are lost for eternity!", True, (255, 255, 255))
        rect = text.get_rect(center=(175, 120))
        self.screen.blit(text, rect)
        pygame.display.flip()
        self.show_repeat_menu()

    def show_repeat_menu(self, options=["Try again", "Back to menu"]):
        self.selected_option = 0
        self.options = options
        self.menu_rects = []
        for i, option in enumerate(self.options):
            text = pygame.font.Font(None, 36).render(option, True, (255, 255, 255))
            rect = text.get_rect(center=(175, 180 + i * 50))
            self.screen.blit(text, rect)
            self.menu_rects.append(rect)
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected_option == 0:
                            self.key_sprite = pygame.image.load("key.png")
                            self.key_sprite = pygame.transform.scale(self.key_sprite, (16, 16))
                            self.run_game()
                        elif self.selected_option == 1:
                            self.show_menu()
            for i, rect in enumerate(self.menu_rects):
                if i == self.selected_option:
                    pygame.draw.rect(self.screen, (255, 128, 0), rect, 3)
                else:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 3)
            pygame.display.flip()

    def show_menu(self):
        self.screen.fill((0, 0, 0))
        menu = MainMenu()
        level_choice = menu.run_menu(self.screen)
        if level_choice is not None:
            levels = [
                [
                    "WWWWWWWWWWWWWWWWWWWWW",
                    "W                   W",
                    "W         WWWWWW    W",
                    "W   WWWW       W    W",
                    "W   W        WWWW   W",
                    "W WWW  WWWW       K W",
                    "W   W     W W       W",
                    "W   W     W   WWW W W",
                    "W   WWW WWW   W W   W",
                    "W     W   W   W W   W",
                    "WWW   W   WWWWW W   W",
                    "W W      WW         W",
                    "W W   WWWW   WWW    W",
                    "W WWWWW  W     W    W",
                    "W        W          W",
                    "W E                 W",
                    "WWWWWWWWWWWWWWWWWWWWW",
                ],
                [
                    "WWWWWWWWWWWWWWWWWWWWW",
                    "W W         WKW     W",
                    "W   WWWWWWW W WWW W W",
                    "W   W     W   W   W W",
                    "W W W WWW WWWWW WWW W",
                    "W W W   W W   W   WEW",
                    "W W WWW W W W WWW WWW",
                    "W   W   W   W   W   W",
                    "W WWW WWWWWWWWW WWW W",
                    "W W   W     W W W   W",
                    "W W W W WWW W W W WWW",
                    "W W W W W W W W W   W",
                    "W W WWW W W W W W W W",
                    "W W       W W   W W W",
                    "W WWWWWWW W WWW WWW W",
                    "W       W W   W W   W",
                    "WWWWWWW W WWW W W WWW",
                    "W W   W W W   W W   W",
                    "W W W W WWW WWW WWW W",
                    "W   W       W       W",
                    "WWWWWWWWWWWWWWWWWWWWW",
                ],
                [
                    "WWWWWWWWWWWWWWWWWWWWW",
                    "W   W     KWW   W   W",
                    "W   W W  WWW  W W W W",
                    "W   W WW EW  WW   W W",
                    "W WWW W   W WWWWW W W",
                    "W     W  WW    W  W W",
                    "W W WWWW  WWWW W  W W",
                    "W W W    WW    W  W W",
                    "W W WWW   W WWWW WW W",
                    "W W   W WWW W W  W  W",
                    "W WWW W     W   WWW W",
                    "W   W WWWWWWWWWWW   W",
                    "WWW W   WW  W       W",
                    "W   W      WW W WWWWW",
                    "W WWWWWWWW    W     W",
                    "W W      W WWWWWWWW W",
                    "W W WWW WW   W      W",
                    "W W W W  WWW W WWWWWW",
                    "W   W   WW   W      W",
                    "WWWWWWWWWWWWWWWWWWWWW",
                ],
                [
                    "WWWWWWWWWWWWWWWWWWWWW",
                    "W   W   W       W   W",
                    "W   W W W W WWW WWW W",
                    "W W   W   W   W     W",
                    "W WWWWWWWWWWW WWWWW W",
                    "W     W   W   W   W W",
                    "W WWWWW W W W W W WWW",
                    "W W     W W WKW W   W",
                    "W W WWWWW W WWW WWW W",
                    "W W   W W W WE  W   W",
                    "WWWWW W W W WWWWW WWW",
                    "W     W     W   W W W",
                    "W WWWWWWWWW WWW W W W",
                    "W         W     W   W",
                    "W WWWWWWW WWW WWWWW W",
                    "W W       W   W   W W",
                    "W W WWWWWWWWWWW W W W",
                    "W W W           W W W",
                    "W W W WWWWWWWWWWW W W",
                    "W W             W   W",
                    "WWWWWWWWWWWWWWWWWWWWW",
                ],
                [
                    "WWWWWWWWWWWWWWWWWWWWW",
                    "W             W     W",
                    "W  WWWWWWWWWW W WWWWW",
                    "W   W     W   W     W",
                    "WWWWW WWW W WWWWWWW W",
                    "W     W   W WK    W W",
                    "W W WWWWWWW WWW W W W",
                    "W W   W     W   W   W",
                    "W WWW W WWWWW WWWWW W",
                    "W   W   W       W   W",
                    "WWW WWWWWWWWW W W WWW",
                    "WEW W       W W W   W",
                    "W W WWW WWW WWW WWW W",
                    "W W W   W W     W W W",
                    "W W W WWW WWWWWWW W W",
                    "W W   W     W     W W",
                    "W WWWWW WWW W WWW W W",
                    "W     W W W W W W   W",
                    "W WWWWW W W W W WWWWW",
                    "W         W         W",
                    "WWWWWWWWWWWWWWWWWWWWW",
                ],
            ]
            if level_choice < len(levels):
                self.running = True
                self.level = levels[level_choice]
                self.walls = []
                self.load_level()
                self.run_game()

    def pause_menu(self):
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        self.show_repeat_menu(["Resume", "Back to menu"])


# Run the game
if __name__ == "__main__":
    game = Game([
        "WWWWWWWWWWWWWWWWWWWW",
    ])
    game.show_menu()
