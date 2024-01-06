import processTask
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
    def input_version(pre_version: PackageVersion) -> PackageVersion or None:
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

        return version_str + str(new_version_code)

    def modify_packages_lock_json(self, package_version: PackageVersion, set_process):
        set_process(0.5)

        project_path = self.runtime.get_cur_project_path()
        packages_lock_json_path = utils.get_packages_lock_json_path(project_path)
        with open(packages_lock_json_path, "r") as f:
            package_json = json.load(f)
        p = package_json["dependencies"][utils.PACKAGE_NAME]
        p["version"] = package_version.to_str()
        with open(packages_lock_json_path, "w", newline="\n") as f:
            f.write(json.dumps(package_json, indent=2))
            f.write("\n")
            f.flush()

        set_process(1)

    def modify_manifest_json(self, package_version: PackageVersion, set_process):
        set_process(0.5)

        project_path = self.runtime.get_cur_project_path()
        manifest_json_path = utils.get_manifest_json_path(project_path)
        with open(manifest_json_path, "r") as f:
            manifest_json = json.load(f)
        d = manifest_json["dependencies"]
        d[utils.PACKAGE_NAME] = package_version.to_str()
        with open(manifest_json_path, "w", newline="\r\n") as f:
            f.write(json.dumps(manifest_json, indent=2))
            f.flush()

        set_process(1)

    def add_json_change_to_git(self, set_process):
        set_process(0.3)

        self.runtime.execute_git_command(
            [
                "add",
                self.runtime.get_cur_project_path() + "/Packages/manifest.json",
            ]
        )

        set_process(0.6)

        self.runtime.execute_git_command(
            [
                "add",
                self.runtime.get_cur_project_path() + "/Packages/packages-lock.json",
            ]
        )

        set_process(1)

    def commit_change(self, new_version: PackageVersion, set_process):
        set_process(0.5)

        self.runtime.execute_git_command(
            [
                "commit",
                "-m",
                "feat：【renderframework】更新至" + new_version.to_str(),
            ]
        )

        set_process(1)

    def modify_package_in_unity(self):
        print()

        if not self.package_state.in_cache:
            print(utils.color("包不在Cache中，无法修改", 31))
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        new_version = self.input_version(self.package_state.version)
        if not new_version:
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        if not processTask.run_step(
                "修改packages-lock.json配置: ",
                lambda set_process: self.modify_packages_lock_json(new_version, set_process),
        ):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        if not processTask.run_step(
                "修改manifest.json配置: ",
                lambda set_process: self.modify_manifest_json(new_version, set_process),
        ):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        if not processTask.run_step("将修改添加到git: ", lambda set_process: self.add_json_change_to_git(set_process)):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        if not processTask.run_step("提交修改: ", lambda set_process: self.commit_change(new_version, set_process)):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        print(utils.color("修改成功", 32))
        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)

    def modify_packages_json(self, new_version: PackageVersion, set_process):
        set_process(0.3)

        package_json_path = self.config.rf_path + "/package.json"
        with open(package_json_path, "r") as f:
            package_json = json.load(f)
        package_json["version"] = new_version.to_str()
        with open(package_json_path, "w", newline="\r\n") as f:
            f.write(json.dumps(package_json, indent=2))
            f.flush()

        set_process(1)

    def modify_package_in_rf(self):
        print()

        new_version = self.input_version(self.package_state.rf_version)
        if not new_version:
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return
        if new_version == self.package_state.rf_version:
            print(utils.color("版本号未改变，取消操作", 31))
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        if not processTask.run_step("修改packages.json配置: ", lambda set_process: self.modify_packages_json(new_version, set_process)):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        def commit_package_json_change(v: PackageVersion, set_process):
            set_process(0.1)
            self.runtime.execute_git_command_rf(["add", self.config.rf_path + "/package.json"])
            set_process(0.6)
            self.runtime.execute_git_command_rf(
                [
                    "commit",
                    "-m",
                    "feat：【版本】更新至" + v.to_str(),
                ]
            )
            set_process(1)

        if not processTask.run_step("提交修改: ", lambda set_process: commit_package_json_change(new_version, set_process)):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        print(utils.color("修改成功", 32))
        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
        return

    def register_menu(self):
        self.menu_mgr.register_menu(
            MenuNames.MODIFY_PACKAGE_JSON_MENU,
            Menu(
                "选择要修改的包",
                [
                    KeyAction("r", "RF工程", self.modify_package_in_rf),
                    KeyAction("e", "Unity工程", self.modify_package_in_unity),
                    KeyAction("q", "返回", lambda: self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)),
                ],
                new_line=True,
            ),
        )
