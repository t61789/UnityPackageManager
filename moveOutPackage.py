import processTask
from runtime import *
from packageState import *


class MoveOutPackage:
    
    def __init__(self, package_state: PackageState, menu_mgr: MenuMgr, runtime: Runtime):
        self.package_state = package_state
        self.menu_mgr = menu_mgr
        self.runtime = runtime

    def add_framework_change_to_git(self, set_process, add_packages_lock_also: bool = False):
        set_process(0.5)
        package_path = utils.get_package_path(self.runtime.get_cur_project_path(), False, self.package_state.version)
        _, stderr = self.runtime.execute_git_command(["add", package_path + "/*"])

        if "error: " in stderr:
            raise Exception(stderr)

        if add_packages_lock_also:
            packages_path = utils.get_unity_packages_path(self.runtime.get_cur_project_path())
            _, stderr = self.runtime.execute_git_command(["add", packages_path + "/packages-lock.json"])

        set_process(1)

    def modify_package_lock_json(self, set_process):
        packages_lock_json_path = utils.get_packages_lock_json_path(self.runtime.get_cur_project_path())
        with open(packages_lock_json_path) as f:
            packages_lock_json = json.load(f)

        set_process(0.3)

        package_json = packages_lock_json["dependencies"][utils.PACKAGE_NAME]
        package_json["source"] = "embedded"
        package_json["version"] = "file:" + utils.get_package_full_name(self.package_state.version)
        package_json["depth"] = 0
        if "url" in package_json:
            del package_json["url"]

        set_process(0.6)

        with open(packages_lock_json_path, "w", newline="\n") as f:
            f.write(json.dumps(packages_lock_json, indent=2))
            f.write("\n")
            f.flush()

        set_process(1)

    def move_out_package(self, commit: bool = False):
        print()

        # 移出文件 ------------------------------------------
        def step0(set_process):
            src = utils.get_package_path(self.runtime.get_cur_project_path(), True, self.package_state.version)
            dest = utils.get_package_path(self.runtime.get_cur_project_path(), False, self.package_state.version)
            utils.copy_directory(src, dest, True, set_process)
            return None

        if not processTask.run_step("移出Package文件: ", step0):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        # 修改json ------------------------------------------
        if not processTask.run_step("修改packages-lock.json配置: ", self.modify_package_lock_json):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        # 将修改添加到git ------------------------------------------
        def step2(set_process):
            self.add_framework_change_to_git(set_process, True)

        if not processTask.run_step("将修改添加到git: ", step2):
            self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
            return

        # 提交 ------------------------------------------
        if commit:

            def step3(set_process):
                set_process(0.5)
                _, stderr = self.runtime.execute_git_command(["commit", "-m", "feat：【RF】移出包体"])
                if "error: " in stderr:
                    raise Exception(stderr)
                set_process(1)

            if not processTask.run_step("提交修改到git: ", step3):
                self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)
                return

        """
        # 重新生成项目文件 ------------------------------------------
        def step4(setProcess):
            setProcess(0.1)
            program.syncProjectFiles()
            setProcess(1)

        processTask.runStep("重新生成项目文件: ", step4)
        """

        print(utils.color("移出完成", 32))
        self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)

    def try_switch_move_out_package_menu(self):
        print()

        if not self.package_state.in_cache:
            print(utils.color("Package不在Cache中，无需移出", 33))
            return

        if not self.package_state.exists:
            print(utils.color("Cache内不存在本地Package文件，无需移出，可以使用Unity重新下载", 33))
            return

        self.menu_mgr.switch_menu(MenuNames.MOVE_OUT_PACKAGE_MENU)
        
    def register_menu(self):
        self.menu_mgr.register_menu(
            MenuNames.MOVE_OUT_PACKAGE_MENU,
            Menu(
                "是否提交修改？",
                [
                    KeyAction("a", "不提交", self.move_out_package),
                    KeyAction("s", "提交", lambda: self.move_out_package(True)),
                    KeyAction("q", "返回", lambda: self.menu_mgr.switch_menu(MenuNames.MAIN_MENU)),
                ],
                0,
            ),
        )
