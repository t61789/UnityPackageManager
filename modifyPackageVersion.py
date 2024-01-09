import processTask
import utils
from config import *
from menuMgr import *
from runtime import *


class ModifyPackageVersion:
    def __init__(self, package_state: PackageState, menu_mgr: MenuMgr, cur_config: Config, runtime: Runtime):
        self.package_state = package_state
        self.menu_mgr = menu_mgr
        self.config = cur_config
        self.runtime = runtime

    @staticmethod
    def __input_version(pre_version: PackageVersion) -> PackageVersion or None:
        print()
        version_str = pre_version.to_str()
        last_dot_index = version_str.rfind(".")
        version_str = version_str[0: last_dot_index + 1]
        utils.print_inline("新的版本号：" + version_str)

        input_str = ""
        while True:
            k = readchar.readkey()
            if k == readchar.key.ESC:
                print(utils.color("\n取消输入", 31))
                return None
            if k == readchar.key.ENTER:
                print()
                print()
                break
            if k == readchar.key.BACKSPACE:
                if len(input_str) > 0:
                    input_str = input_str[:-1]
                    utils.print_inline("\x1b[1D \x1b[1D")
            else:
                utils.print_inline(utils.color(k, 33))
                input_str += k

        try:
            new_version_code = int(input_str)
            if new_version_code <= 0:
                raise Exception()
        except Exception:
            print(utils.color("\n无效输入", 31))
            return None

        return PackageVersion.load_from_str(version_str + str(new_version_code))

    def __modify_packages_lock_json(self, package_version: PackageVersion, set_process):
        set_process(0.5)

        project_path = self.runtime.get_cur_project_path()
        packages_lock_json_path = utils.get_packages_lock_json_path(project_path)
        with open(packages_lock_json_path, "r") as f:
            package_json = json.load(f)
        p = package_json["dependencies"][self.config.package_name]
        p["version"] = package_version.to_str()
        with open(packages_lock_json_path, "w", newline="\n") as f:
            f.write(json.dumps(package_json, indent=2))
            f.write("\n")
            f.flush()

        set_process(1)

    def __modify_manifest_json(self, package_version: PackageVersion, set_process):
        set_process(0.5)

        project_path = self.runtime.get_cur_project_path()
        manifest_json_path = utils.get_manifest_json_path(project_path)
        with open(manifest_json_path, "r") as f:
            manifest_json = json.load(f)
        d = manifest_json["dependencies"]
        d[self.config.package_name] = package_version.to_str()
        with open(manifest_json_path, "w", newline="\r\n") as f:
            f.write(json.dumps(manifest_json, indent=2))
            f.flush()

        set_process(1)

    def __modify_package_in_unity(self):
        print()

        if not self.package_state.in_cache:
            print(utils.color("包不在Cache中，无法修改", 31))
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        new_version = self.__input_version(self.package_state.version)
        if not new_version:
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return
        if new_version == self.package_state.version:
            print(utils.color("版本号未改变，取消操作", 31))
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        def task0():
            return processTask.run_step(
                "修改packages-lock.json配置: ",
                lambda set_process: self.__modify_packages_lock_json(new_version, set_process))
        
        def task1():
            return processTask.run_step(
                "修改manifest.json配置: ",
                lambda set_process: self.__modify_manifest_json(new_version, set_process))

        def task2():
            return processTask.run_cmd_task(
                "将添加packages-lock.json修改到git: ",
                self.runtime.get_cur_project_path(),
                ["git", "add", "Packages/packages-lock.json"],
                stay_time=0.1)
    
        def task3():
            return processTask.run_cmd_task(
                "将添加manifest.json修改到git: ",
                self.runtime.get_cur_project_path(),
                ["git", "add", "Packages/manifest.json"],
                stay_time=0.1)
        
        def task4():
            return processTask.run_cmd_task(
                "提交版本修改",
                self.runtime.get_cur_project_path(),
                ["git", "commit", "-m", "feat：【renderframework】更新至" + new_version.to_str()])
        
        all_task_succeed = processTask.run_tasks([task0, task1, task2, task3, task4])
        if all_task_succeed:
            utils.print_hint("[green]修改成功[/]")

        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)

    def __modify_packages_json(self, new_version: PackageVersion, set_process):
        set_process(0.3)

        package_json_path = self.config.rf_path + "/package.json"
        with open(package_json_path, "r") as f:
            package_json = json.load(f)
        package_json["version"] = new_version.to_str()
        with open(package_json_path, "w", newline="\r\n") as f:
            f.write(json.dumps(package_json, indent=2))
            f.flush()

        set_process(1)

    def __modify_package_in_rf(self):
        print()

        new_version = self.__input_version(self.package_state.rf_version)
        if not new_version:
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return
        if new_version == self.package_state.rf_version:
            utils.print_hint("[yellow]版本号未改变，取消操作[/]")
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        def task0():
            return processTask.run_step(
                "修改packages.json配置: ",
                lambda set_process: self.__modify_packages_json(new_version, set_process))

        def task1():
            return processTask.run_cmd_task(
                "添加package.json修改到缓冲区",
                self.config.rf_path,
                ["git", "add", "package.json"])

        def task2():
            return processTask.run_cmd_task(
                "提交版本修改",
                self.config.rf_path,
                ["git", "commit", "-m", "feat：【版本】更新至" + new_version.to_str()])
        
        all_task_succeed = processTask.run_tasks([task0, task1, task2])
        if all_task_succeed:
            utils.print_hint("[green]修改成功[/]")
            return

        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
        return

    def register_menu(self):
        self.menu_mgr.register_menu(
            MenuNames.MODIFY_PACKAGE_JSON_MENU,
            Menu(
                "选择要修改的包",
                [
                    KeyAction("r", "RF工程", self.__modify_package_in_rf),
                    KeyAction("e", "Unity工程", self.__modify_package_in_unity),
                    KeyAction("q", "返回", lambda: self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)),
                ],
                new_line=True,
            ),
        )
