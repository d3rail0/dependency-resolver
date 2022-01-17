import os, time, pygame
from src.states.menu import Menu

class Resolver():

    def __init__(self) -> None:
        pygame.init()

        self.VIEW_W  , self.VIEW_H   = 800, 600
        self.SCREEN_W, self.SCREEN_H = 800, 600

        self.canvas          = pygame.Surface((self.VIEW_W, self.VIEW_H))
        self.display_surface = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.RESIZABLE)

        self.is_running  = True
        self.state_stack = []
        self.actions = {"left": False, "right": False, "up" : False, "down" : False, "action1" : False, "action2" : False}
        self.dt, self.prev_time = 0, 0

        self.mouse_x, self.mouse_y = 0, 0

        self.__init_assets()
        self.__init_states()

    def main_loop(self) -> None:
        while self.is_running:
            self.__update_dt()
            self.__capture_events()
            self.__update()
            self.__render()

    def __capture_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_x, self.mouse_y = event.pos
                self.actions['action1'] = True
                           
    def __update_dt(self) -> None:
        now            = time.time()
        self.dt        = now - self.prev_time
        self.prev_time = now

    def __update(self) -> None:
        self.state_stack[-1].update(self.dt, self.actions)

    def __render(self) -> None:
        self.state_stack[-1].render(self.canvas)
        self.display_surface.blit(pygame.transform.scale(self.canvas, self.display_surface.get_size()), (0,0))
        pygame.display.flip()
    
    def __init_assets(self) -> None:
        self.assets_dir = os.path.join("./assets")
        self.font_dir   = os.path.join(self.assets_dir, "font")
        self.font       = pygame.font.SysFont("consolas", 14)

    def __init_states(self) -> None:
        self.menu_state = Menu(self)
        self.state_stack.append(self.menu_state)

    def draw_text(self, surface, text, color, x, y) -> None:        
        text_surface     = self.font.render(text, True, color)
        text_rect        = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)

    def reset_keys(self) -> None:
        for action in self.actions:
            self.actions[action] = False
