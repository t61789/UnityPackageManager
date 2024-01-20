import git_commands
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
            utils.print_hint("[red]取消操作[/]")
            return
        
        all_succeed = git_commands.GitCommands.remove_all_modifies(self.runtime.get_cur_project_path())
        if all_succeed:
            utils.print_hint("[green]移除所有修改成功[/]")
