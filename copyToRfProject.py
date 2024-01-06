import processTask
from runtime import *


class CopyToRfProject:

    def __init__(self, package_state: PackageState, cur_config: Config, menu_mgr: MenuMgr, runtime: Runtime):
        self.package_state = package_state
        self.config = cur_config
        self.menu_mgr = menu_mgr
        self.runtime = runtime

    def copy_to(self):
        unity_project_path = self.runtime.get_cur_project_path()
        rf_path = self.config.rf_path

        print()

        def step(set_process):
            utils.clear_directory(rf_path, set_process)

        if not processTask.run_step("清空RF工程: ", step):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        def step(set_process):
            package_path = utils.get_package_path(unity_project_path, False, self.package_state.version)
            utils.copy_directory(package_path, rf_path, False, set_process)

        if not processTask.run_step("复制Package到RF工程: ", step):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        print(utils.color("复制成功", 32))

    def start_copy(self):
        if self.package_state.in_cache:
            print(utils.color("Package未移出，无法复制", 31))
            return

        if self.package_state.version != self.package_state.rf_version:
            print()
            confirm = MenuMgr.confirm_menu(utils.color("BN_Package版本与RF_Package版本不一致，是否继续？", 33))
            print()
            if not confirm:
                print(utils.color("取消操作", 31))
                return

        # TODO 检查RF工程git是否有修改, 用git status

        self.copy_to()
