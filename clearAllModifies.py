import menuMgr
import processTask
from runtime import *


class ClearAllModifies:

    def __init__(self, menu_mgr: menuMgr.MenuMgr, runtime: Runtime):
        self.menu_mgr = menu_mgr
        self.runtime = runtime

    def clear_all_modifies(self):
        print()

        if not menuMgr.MenuMgr.confirm_menu("确认要移除所有的修改吗？"):
            print(utils.color("取消操作", 31))
            return

        def step0(set_process):
            set_process(0.5)
            self.runtime.execute_git_command(["add", "."])
            set_process(1)

        if not processTask.run_step("添加所有修改: ", step0):
            return

        def step1(set_process):
            set_process(0.3)
            self.runtime.execute_git_command(["reset", "--hard", "head"])
            set_process(1)

        if not processTask.run_step("移除所有修改: ", step1):
            return

        print(utils.color("移除所有修改成功", 32))
