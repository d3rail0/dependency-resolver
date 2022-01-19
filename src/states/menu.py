from __future__ import annotations
from src.states.state import *
from src.states.scan import Scan
from src.ui.button import *
from src.utils import util
import src.ui.colors as colors 

class Menu(State):

    CMD_CHOOSE = "cmdChoose"
    CMD_EXIT = "cmdExit"


    def __init__(self, resolver):
        super().__init__(resolver)
        self._init_ui()                
        
    def _init_ui(self):
        self.buttons: dict[str, Button] = {}

        common_props = ButtonProperties(
                colors.DARK_GREEN,
                colors.WHITE,
                self.resolver.font,
                colors.DARK_GREEN_HOVER
            )

        btn_width = 140
        btn_height = 50

        center_x = self.resolver.VIEW_W/2 - btn_width/2
        center_y = self.resolver.VIEW_H/2 - btn_height/2 - btn_height*1.5

        self.buttons[self.CMD_CHOOSE] = Button(
            center_x, center_y, btn_width, btn_height, common_props, "Start"
        )
        self.buttons[self.CMD_EXIT] = Button(
            center_x, center_y + len(self.buttons)*btn_height*1.5, btn_width, btn_height, common_props, "Exit"
        )

    def _update_ui(self, dt, actions):
        for control_key in self.buttons:
            self.buttons.get(control_key).update(
                dt, self.resolver.mouse_x, self.resolver.mouse_y, actions["m_up"]
            )

    def update(self, delta_time, actions):
        self._update_ui(delta_time, actions)

        if self.buttons[self.CMD_CHOOSE].is_clicked():

            target_project_dir = self.resolver.find_directory()

            if target_project_dir:
                new_state = Scan(self.resolver, target_project_dir)
                new_state.enter_state()
            else:
                self.resolver.show_error("Project directory", "You haven't selected a project directory.")
                
            self.resolver.focus()

        elif self.buttons[self.CMD_EXIT].is_clicked():
            self.exit_state()

        self.resolver.reset_keys()

    def _render_ui(self, display):
        for control_key in self.buttons:
            self.buttons.get(control_key).render(display)

    def render(self, display):
        display.fill(colors.BLACK)
        self._render_ui(display)