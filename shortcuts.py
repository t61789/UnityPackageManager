import keyboard
import utils
from config import Config


class Shortcuts:
    def __init__(self, cur_config: Config):
        self.config = cur_config

    def on_hit(self, e):
        for key in self.config.show_window_shortcut:
            if not keyboard.is_pressed(key):
                return
        utils.show_window()

    def start(self):
        keyboard.hook(lambda x: self.on_hit(x))

    def dispose(self):
        keyboard.unhook_all()
