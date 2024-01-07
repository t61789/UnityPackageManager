import copyToRfProject
import deleteShaderCache
import git
import moveOutPackage
from clearAllModifies import *
from git import GitCommands
from runtime import *


class MainMenu:

    def __init__(self, package_state: PackageState, cur_config: Config, runtime: Runtime):
        self.package_state = package_state
        self.config = cur_config
        self.runtime = runtime

    def __get_candidate_projects(self) -> str | None:
        project_num = len(self.config.project_paths)
        if project_num == 0:
            return None
        s = "[Unity项目候选]\t\t"
        for i in range(project_num):
            byname = self.config.project_paths[i].byname
            if i == self.runtime.cur_project_index:
                byname = utils.color(byname, 34)
            s += byname
            if i != project_num - 1:
                s += " | "
        return s + "\n"

    def get_header(self) -> str:
        project_path = self.config.project_paths[self.runtime.cur_project_index]
        s = "\n"

        s += utils.SPLITER + "\n"

        # Unity项目候选
        s += self.__get_candidate_projects()

        # Unity项目路径
        byname = utils.color(project_path.byname, 34)
        s += "[Unity项目路径]\t\t" + byname + " " + project_path.path + "\n"

        # RenderFramework路径
        s += "[RenderFramework路径]\t" + self.config.rf_path + "\n"

        package_state = self.package_state

        # Package位置
        if package_state.in_cache:
            package_position = utils.color("Cache", 32)
            if not package_state.exists:
                package_position += utils.color("（不存在本地文件）", 35)
        else:
            package_position = utils.color("Packages", 31)

        s += "[Package位置]\t\t" + package_position + "\n"

        bn_version = package_state.version
        rf_version = package_state.rf_version

        # BN Package版本
        s += "[BN_Package版本]\t" + bn_version.to_str(33) + "\n"

        # RF Package版本
        if rf_version == bn_version:
            need_back = False
            need_update = False
        else:
            need_back = rf_version.is_higher(bn_version)
            need_update = not need_back

        if need_update:
            version_note = utils.color(" [需要更新]", 31)
        elif need_back:
            version_note = utils.color(" [需要回退]", 31)
        else:
            version_note = ""
        s += "[RF_Package版本]\t" + rf_version.to_str(33) + version_note + "\n"
        return s

    def register_menu(self, menu_mgr: MenuMgr):
        copy_to_rf_project = copyToRfProject.CopyToRfProject(self.package_state, self.config, menu_mgr, self.runtime)
        move_out_package = moveOutPackage.MoveOutPackage(self.package_state, menu_mgr, self.runtime)
        delete_shader_cache = deleteShaderCache.DeleteShaderCache(self.runtime)
        clear_all_modifies = ClearAllModifies(menu_mgr, self.runtime)
        git_commands = GitCommands(self.package_state, self.config)
            
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
                    KeyAction("q", "退出", utils.exit_application),
                    # TODO 进阶操作
                ],
            ),
        )
