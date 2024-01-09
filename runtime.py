import processTask
import utils

from packageState import *
from config import *
from menuMgr import *
from rich import box
from rich.table import Table


class Runtime:
    def __init__(self, cur_config: Config, menu_mgr: MenuMgr, package_state: PackageState):
        self.cur_project_index = 0
        self.config = cur_config
        self.menu_mgr = menu_mgr
        self.package_state = package_state
        
    def switch_project_index(self):
        self.cur_project_index = (self.cur_project_index + 1) % max(len(self.config.project_paths), 1)
        print("开始切换到第" + str(self.cur_project_index) + "个工程")
        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)

    def get_cur_project_path(self):
        return self.config.project_paths[self.cur_project_index].path

    def sync_project_files(self):
        return utils.execute_cmd(
            [
                self.config.unity_editor_path,
                "-projectPath",
                self.get_cur_project_path(),
                "-batchmode",
                "-quit",
                "-executeMethod",
                "UnityEditor.SyncVS.SyncSolution",
            ],
            self.get_cur_project_path(),
        )
    
    def get_git_status(self):
        succeed, std_out, std_err = processTask.execute_cmd_simple(["git", "status", "--porcelain"], self.get_cur_project_path())
        if succeed:
            has_changes = len(std_out) > 0
        else:
            has_changes = True
        succeed, std_out, std_err = processTask.execute_cmd_simple(["git", "branch", "--show-current"], self.get_cur_project_path())
        if succeed:
            branch = std_out
        else:
            branch = "UNKNOWN_BRANCH"
        return has_changes, branch
            

    def initialize_tick(self):
        try:
            self.config.load_config()
        except Exception as e:
            utils.log("读取配置文件出错: \n" + str(e), utils.LogType.Error)
            self.menu_mgr.switch_menu(MenuNames.CONFIG_ERROR_MENU)
            return

        try:
            self.package_state.analyze_package_state(self.get_cur_project_path())
        except Exception as e:
            utils.log("分析项目结构出错：\n" + str(e), utils.LogType.Error)
            self.menu_mgr.switch_menu(MenuNames.PACKAGE_ERROR_MENU)
            return

    def execute_git_command(self, args: [str]):
        return utils.execute_cmd(["git"] + args, self.get_cur_project_path())

    def execute_git_command_rf(self, args: [str]):
        return utils.execute_cmd(["git"] + args, self.config.rf_path)

    def execute_git_command_with_exp(self, args: [str]):
        _, stderr = self.execute_git_command(args)
        if "error: " in stderr:
            raise Exception(stderr)

    def execute_git_command_rf_with_exp(self, args: [str]):
        _, stderr = self.execute_git_command_rf(args)
        if "error: " in stderr:
            raise Exception(stderr)

    @staticmethod
    def check_work_space_has_changed(path: str) -> bool:
        stdout, stderr = utils.execute_cmd(["git", "status", "--porcelain"], path)
        if "error: " in stderr:
            raise Exception(stderr)
        return len(stdout) > 0
    
    @staticmethod
    def get_header(s):
        table = Table(title="\nUnity Package Manager", box=box.ROUNDED, show_header=False)
        table.add_column()
        table.add_row(s)
        return table
    
    def register_menu(self):
        self.menu_mgr.register_menu(
            MenuNames.CONFIG_ERROR_MENU,
            Menu(
                lambda: Runtime.get_header("读取配置文件出错"),
                [
                    KeyAction("w", "重新读取配置文件", None),
                    KeyAction("v", "切换工程", self.switch_project_index),
                    KeyAction("q", "退出", utils.exit_application),
                ],
            ),
        )

        self.menu_mgr.register_menu(
            MenuNames.PACKAGE_ERROR_MENU,
            Menu(
                lambda: Runtime.get_header("读取项目信息出错"),
                [
                    KeyAction("w", "重新读取项目信息", None),
                    KeyAction("v", "切换工程", self.switch_project_index),
                    KeyAction("q", "退出", utils.exit_application),
                ],
            ),
        )
