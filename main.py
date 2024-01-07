import os

import utils
from runtime import Runtime
from mainMenu import MainMenu
from menuMgr import *
from packageState import PackageState
from config import Config
from modifyPackageVersion import ModifyPackageVersion
from moveOutPackage import MoveOutPackage
from shortcuts import *

# TODO 兼容WindowsTerminal路径
os.system("")

cur_config = Config()
package_state = PackageState(cur_config)
menu_mgr = MenuMgr()
runtime = Runtime(cur_config, menu_mgr, package_state)
main_menu = MainMenu(package_state, cur_config, runtime)
modify_package_version = ModifyPackageVersion(package_state, menu_mgr, cur_config, runtime)
move_out_package = MoveOutPackage(package_state, menu_mgr, runtime, cur_config)
utils.config = cur_config
shortcuts = Shortcuts(cur_config)
shortcuts.start()

main_menu.register_menu(menu_mgr)
modify_package_version.register_menu()
move_out_package.register_menu()
runtime.register_menu()

menu_mgr.on_tick_start(runtime.initialize_tick)

menu_mgr.switch_menu(MenuNames.MAIN_MENU)
menu_mgr.start_menu()
