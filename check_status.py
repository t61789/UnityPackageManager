import os

from rich.table import Table

import processTask
import utils
from runtime import Runtime


class CheckStatus:
    def __init__(self, runtime: Runtime):
        self.runtime = runtime

    def check(self):
        stdout_list = []
        succeed = processTask.run_cmd_task("查询当前修改", self.runtime.get_cur_project_path(), ["git", "status", "-s"],
                                           stdout_list=stdout_list)
        if not succeed:
            utils.print_hint("[red]查询当前修改失败[/]")
            return
        
        if len(stdout_list) == 0:
            utils.print_hint("[green]当前没有修改[/]")
            return

        file_names = []
        for i in range(len(stdout_list)):
            line = stdout_list[i]
            file_name = os.path.basename(line).strip()
            modified = line.split(" ")[1]
            file_names.append(f"{modified} {file_name}")

        column_num = 4
        table = Table(title=None, show_header=False, padding=0, show_lines=False, show_footer=False)
        for i in range(column_num):
            table.add_column()

        cur_row = []
        while len(file_names) > 0:
            for i in range(column_num):
                if len(file_names) > 0:
                    cur_row.append(file_names.pop(0))
                else:
                    cur_row.append("")
            table.add_row(*cur_row)
            cur_row.clear()

        utils.print(table)
