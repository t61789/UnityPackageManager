import git
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
        
        all_succeed = git.GitCommands.remove_all_modifies(self.runtime.get_cur_project_path())
        if all_succeed:
            print(utils.color("移除所有修改成功", 32))
