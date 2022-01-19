import sys, os, time
import src.utils.util as util 

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

# GUI
import tkinter
from tkinter import messagebox
from tkinter import filedialog as fd

# Render engine
import pygame

# State
from src.states.menu import Menu

class Resolver():

    def __init__(self) -> None:
        pygame.init()

        # Don't show tkinter window
        tkinter.Tk().withdraw()
        
        self.__init_assets()

        icon = pygame.image.load(os.path.join(self.assets_dir, "icon.ico"))
        pygame.display.set_icon(icon)

        self.VIEW_W  , self.VIEW_H   = 1024, 860
        self.SCREEN_W, self.SCREEN_H = 1024, 860

        self.canvas          = pygame.Surface((self.VIEW_W, self.VIEW_H))
        self.display_surface = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.RESIZABLE)

        self.is_running  = True
        self.state_stack = []
        self.fps_list    = []
        self.actions     = {"left": False, "right": False, "up" : False, "down" : False, "m_down" : False, "m_up" : False, "escape": True}
        
        self.dt     , self.prev_time = 0, 0
        self.mouse_x, self.mouse_y   = 0, 0
        
        self.__init_states()
        self.__update_interpolators()

    def main_loop(self) -> None:
        while self.is_running:
            self.__update_dt()
            self.__capture_events()
            self.__update()

            # Exit cleanly
            if len(self.state_stack)==0:
                self.is_running = False
                break

            self.__render()

    def __update_interpolators(self):
        self.interp_x = util.make_interpolator([0, self.display_surface.get_size()[0]], [0, self.VIEW_W])
        self.interp_y = util.make_interpolator([0, self.display_surface.get_size()[1]], [0, self.VIEW_H])

    def __fix_mouse_pos(self):        
        self.mouse_x = int(self.interp_x(self.mouse_x))
        self.mouse_y = int(self.interp_y(self.mouse_y))

    def __capture_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_x, self.mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:                
                self.mouse_x, self.mouse_y = event.pos
                self.actions['m_down'] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_x, self.mouse_y = event.pos
                self.actions['m_up'] = True
            elif event.type == pygame.WINDOWRESIZED:
                self.__update_interpolators()
            
            # Handle key presses
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.actions['escape'] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.actions['escape'] = False
                
            
            
            self.__fix_mouse_pos()

    def __update_dt(self) -> None:
        now            = time.time()
        self.dt        = now - self.prev_time
        self.prev_time = now
        self.get_fps()

    def get_fps(self):
        fps = 0
        if self.dt: fps = 1/self.dt
        if len(self.fps_list) == 50:
                self.fps_list.pop(0)
        self.fps_list.append(fps)
        avg_fps = sum(self.fps_list) / len(self.fps_list)
        pygame.display.set_caption('Dependency resolver - FPS: ' + str(round(avg_fps,2)))

    def __update(self) -> None:
        self.state_stack[-1].update(self.dt, self.actions)

    def __render(self) -> None:
        self.state_stack[-1].render(self.canvas)
        self.display_surface.blit(pygame.transform.scale(self.canvas, self.display_surface.get_size()), (0,0))
        pygame.display.flip()
    
    def __init_assets(self) -> None:
        self.assets_dir = os.path.join("assets")
        self.font_dir   = os.path.join(self.assets_dir, "fonts")
        self.font       = pygame.font.Font(os.path.join(self.font_dir, "NunitoRegular-vmABZ.ttf"), 20)

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

    def focus(self) -> None:
        """ Focuses pygame window.
        """
        util.raise_window(pygame.display.get_caption()[0])

    def show_error(self, title, err_txt) -> None:
        messagebox.showerror(title, err_txt)
        self.focus()

    def find_directory(self) -> str:
        """ Opens a file dialog browser.
        Returns: Path to selected directory.
        """
        target_dir = fd.askdirectory()
        self.focus()
        return target_dir