from rich.panel import Panel

import copyToRfProject
import deleteShaderCache
import git
import moveOutPackage
import utils
from clearAllModifies import *
from git import GitCommands
from runtime import *
from rich import box
from rich.table import Table


class MainMenu:

    def __init__(self, package_state: PackageState, cur_config: Config, runtime: Runtime):
        self.package_state = package_state
        self.config = cur_config
        self.runtime = runtime
        self.box = box.Box(
            "╭──╮\n"
            "│  │\n"
            "├─┼┤\n"
            "│  │\n"
            "├─┼┤\n"
            "├─┼┤\n"
            "│  │\n"
            "╰──╯\n"
        )

    def __get_candidate_projects(self):
        project_num = len(self.config.project_paths)
        if project_num == 0:
            return None
        row_name = "[Unity项目候选]"
        s = ""
        for i in range(project_num):
            byname = self.config.project_paths[i].byname
            if i == self.runtime.cur_project_index:
                byname = f"[royal_blue1]{byname}[/]"
            s += byname
            if i != project_num - 1:
                s += " | "
        return [row_name, s]

    def get_header(self):
        project_path = self.config.project_paths[self.runtime.cur_project_index]

        table = Table(title="\nUnity Package Manager", box=self.box, show_header=False)
        table.add_column()
        table.add_column()
        
        # Unity项目候选
        table.add_row(*self.__get_candidate_projects())

        # Unity项目路径
        table.add_row("[Unity项目路径]", f"[royal_blue1]{project_path.byname}[/] {project_path.path}")

        # RenderFramework路径
        table.add_row("[RenderFramework路径]", self.config.rf_path)

        package_state = self.package_state

        # Package位置
        if package_state.in_cache:
            package_position = "[green]Cache[/]"
            if not package_state.exists:
                package_position += "[medium_purple3]（不存在本地文件）[/]"
        else:
            package_position = "[orange3]Packages[/]"

        table.add_row("[Package位置]", package_position)

        bn_version = package_state.version
        rf_version = package_state.rf_version

        # BN Package版本
        table.add_row("[BN_Package版本]", bn_version.to_str("yellow"))

        # RF Package版本
        if rf_version == bn_version:
            need_back = False
            need_update = False
        else:
            need_back = rf_version.is_higher(bn_version)
            need_update = not need_back

        if need_update:
            version_note = " [red][需要更新][/]"
        elif need_back:
            version_note = " [red][需要回退][/]"
        else:
            version_note = ""
        table.add_row("[RF_Package版本]", rf_version.to_str("yellow") + version_note)
        return table

    def register_menu(self, menu_mgr: MenuMgr):
        copy_to_rf_project = copyToRfProject.CopyToRfProject(self.package_state, self.config, menu_mgr, self.runtime)
        move_out_package = moveOutPackage.MoveOutPackage(self.package_state, menu_mgr, self.runtime, self.config)
        delete_shader_cache = deleteShaderCache.DeleteShaderCache(self.runtime)
        clear_all_modifies = ClearAllModifies(menu_mgr, self.runtime)
        git_commands = GitCommands(self.package_state, self.config, self.runtime)

        menu_mgr.register_menu(
            MenuNames.MAIN_MENU,
            Menu(
                self.get_header,
                [
                    KeyAction("w", "重新读取项目信息", None),
                    KeyAction("v", "切换工程", self.runtime.switch_project_index),
                    KeyAction("a", "移出Package", move_out_package.try_switch_move_out_package_menu),
                    KeyAction("r", "修改Package版本", lambda: menu_mgr.switch_menu(MenuNames.MODIFY_PACKAGE_JSON_MENU)),
                    KeyAction("g", "复制Package到RF工程", copy_to_rf_project.start_copy),
                    KeyAction("s", "清除所有修改", clear_all_modifies.clear_all_modifies),
                    KeyAction("b", "删除ShaderCache", delete_shader_cache.delete_shader_cache),
                    KeyAction("z", "匹配RF工程", git_commands.match_rf_version),
                    KeyAction("x", "更新RF工程", git_commands.remove_modifies_and_update_to_latest),
                    KeyAction("q", "隐藏", utils.hide_window),
                    KeyAction("Q", "退出", utils.exit_application),
                    # TODO 进阶操作
                ],
            ),
        )
