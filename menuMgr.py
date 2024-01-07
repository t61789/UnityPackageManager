import msvcrt
from typing import Callable
import readchar
import utils
import rich.console

console = rich.console.Console(highlight=False)
print = console.print


class KeyAction:
    def __init__(self, key: str, describe: str, action: Callable):
        self.key = key
        self.describe = describe
        self.action = action


class Menu:
    def __init__(
            self,
            header: str or Callable,
            key_actions: [KeyAction],
            intent: int = 0,
            default_action: [KeyAction] = None,
            new_line: bool = False,
    ):
        self.header = header
        self.key_actions = key_actions
        self.intent = intent
        self.default_action = default_action
        self.new_line = new_line


class MenuMgr:
    def __init__(self):
        self.menus = {}
        self.cur_menu = Menu(None, None)
        self.key_running = False
        self.on_tick_start_actions = []

    def __execute_key_action(self, key_action: KeyAction):
        if key_action.action:
            self.key_running = True
            key_action.action()
            self.key_running = False

    def find_available_action(self, key_name: str) -> KeyAction | None:
        if self.cur_menu is None or self.key_running:
            return None

        for key_action in self.cur_menu.key_actions:
            if key_name == key_action.key:
                return key_action

        if self.cur_menu.default_action:
            return self.cur_menu.default_action

        return None

    @staticmethod
    def __display_menu(menu: Menu):
        if menu is None:
            return

        if menu.new_line:
            print()

        intend_str = ""
        for i in range(menu.intent):
            intend_str += "  "

        if menu.header:
            if callable(menu.header):
                print(menu.header())
            else:
                print(intend_str + menu.header)

        for keyAction in menu.key_actions:
            print(f"{intend_str}[cyan]{keyAction.key}[/]: {keyAction.describe}")
        utils.print_inline(intend_str + "输入: ")

    def switch_menu(self, menu_name: str):
        self.cur_menu = self.menus[menu_name]

    def register_menu(self, menu_name: str, menu: Menu):
        self.menus[menu_name] = menu

    def on_tick_start(self, action: Callable):
        self.on_tick_start_actions.append(action)

    def remove_on_tick_start(self, action: Callable):
        self.on_tick_start_actions.remove(action)

    def start_menu(self):
        while True:
            for action in self.on_tick_start_actions:
                action()

            MenuMgr.__display_menu(self.cur_menu)

            while True:
                input_key = readchar.readkey()
                key_action = self.find_available_action(input_key)
                if not key_action:
                    continue

                utils.print_inline(input_key + "\n")
                self.__execute_key_action(key_action)

                # 清除在执行命令期间输入的命令
                while msvcrt.kbhit():
                    msvcrt.getch()
                break

    @staticmethod
    def confirm_menu(tile: str) -> bool:
        utils.print_inline(tile + " [E/Q]")
        while True:
            input_key = readchar.readkey()
            if input_key == "e":
                print("e")
                return True
            elif input_key == "q":
                print("q")
                return False


class MenuNames:
    PACKAGE_ERROR_MENU = "pacakgeErrorMenu"
    CONFIG_ERROR_MENU = "configErrorMenu"
    MAIN_MENU = "mainMenu"
    MOVE_OUT_PACKAGE_MENU = "moveOutPackageMenu"
    MODIFY_PACKAGE_JSON_MENU = "modifyPackageJsonMenu"
    COPY_TO_RF_PROJECT_CONFIRM_MENU = "copyToRfProjectConfirmMenu"
