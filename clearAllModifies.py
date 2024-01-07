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

        def task0():
            return processTask.run_cmd_task(
                "添加所有修改",
                self.runtime.get_cur_project_path(),
                ["git", "add", "."],
                show_detail_when_error=True)

        def task1():
            return processTask.run_cmd_task(
                "重置所有修改",
                self.runtime.get_cur_project_path(),
                ["git", "reset", "--hard", "head"],
                show_detail_when_error=True)
        
        all_succeed = processTask.run_tasks([task0, task1])
        if all_succeed:
            print(utils.color("移除所有修改成功", 32))
