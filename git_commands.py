﻿import re

import rich
import menuMgr
import processTask
import utils
from packageState import *
from config import Config
from runtime import Runtime

console = rich.console.Console(highlight=False)
print = console.print


class GitCommands:
    def __init__(self, package_state: PackageState, config: Config, runtime: Runtime):
        self.package_state = package_state
        self.config = config
        self.runtime = runtime

    @staticmethod
    def match_branch_to_upstream(work_space: str):
        success, cur_branch_name, _ = processTask.execute_cmd_simple(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                                                     work_space)
        if not success:
            print("[red]获取当前分支名失败[/]")
            return False
        success, cur_upstream_name, _ = processTask.execute_cmd_simple(
            ["git", "rev-parse", "--abbrev-ref", "HEAD@{upstream}"], work_space)
        if not success:
            print("[red]当前分支未跟踪远程分支[/]")
            return False

        return processTask.run_cmd_task(
            "将跟踪的远程分支强制检出到当前分支",
            work_space,
            ["git", "checkout", "-B", cur_branch_name, cur_upstream_name, "--progress", "-f"])

    @staticmethod
    def update_to_latest(work_space: str):
        def task0():
            return processTask.run_cmd_task("获取更新", work_space, ["git", "fetch", "--progress"])

        def task1():
            return GitCommands.match_branch_to_upstream(work_space)

        return processTask.run_tasks([task0, task1])

    @staticmethod
    def remove_all_modifies(work_space: str):
        stdout_list = []
        succeed = processTask.run_cmd_task("查询是否有修改", work_space, ["git", "status", "-s"], stdout_list=stdout_list)
        
        if not succeed:
            utils.print_hint("[red]获取当前修改失败[/]")
            return False
        else: 
            stdout = "".join(stdout_list)
            stdout = stdout.strip()
            if len(stdout) == 0:
                utils.print_hint("[green]当前没有修改，无需重置[/]")
                return True

        return processTask.run_cmd_task(
            "重置所有修改", 
            work_space,
            ["git", "reset", "--hard", "&&", "git", "clean", "-fd"],
            show_detail_when_error=True, shell=True)

    @staticmethod
    def get_need_push_commits_num(work_space: str):
        std_out = []
        std_err = []
        succeed = processTask.run_cmd_task(
            "获取需要推送的提交数量", work_space, ["git", "rev-list", "--count", "@{upstream}.."], stdout_list=std_out,
            stderr_list=std_err
        )
        if not succeed or len(std_out) == 0:
            return -1
        return int(std_out[0])

    @staticmethod
    def has_un_commit_changes(work_space: str):
        std_out = []
        std_err = []
        succeed = processTask.run_cmd_task("获取未提交的修改", work_space, ["git", "status", "-s"], stdout_list=std_out,
                                           stderr_list=std_err)
        if not succeed:
            return True
        return len(std_out) != 0

    def remove_modifies_and_update_to_latest(self):
        print()

        if not menuMgr.MenuMgr.confirm_menu("确认要移除所有的修改吗？"):
            print(utils.color("取消操作", 31))
            return

        succeed = GitCommands.remove_all_modifies(self.runtime.get_cur_project_path())
        if not succeed:
            return False
        succeed = GitCommands.update_to_latest(self.runtime.get_cur_project_path())
        if not succeed:
            return False
        return True

    def match_rf_version(self):
        target_version = self.package_state.version

        try:
            cur_version = PackageState.get_rf_package_version(self.config.rf_path)
        except Exception:
            return False

        if cur_version == target_version:
            return True

        if GitCommands.get_need_push_commits_num(self.config.rf_path) != 0:
            print("[red]RF工程有未推送的提交，请先推送[/]")
            return False

        if GitCommands.has_un_commit_changes(self.config.rf_path):
            print("[red]RF工程有未提交的修改，请先提交[/]")
            return False

        # 拉最新
        GitCommands.update_to_latest(self.config.rf_path)

        # 读取提交
        grep_match_str = target_version.to_str().replace(".", "\\.")
        std_out = []
        std_err = []
        succeed = processTask.run_cmd_task(
            "读取git提交",
            self.config.rf_path,
            ["git", "--no-pager", "log", f"--grep={grep_match_str}", "--format=%H %s"],
            stdout_list=std_out,
            stderr_list=std_err,
        )

        if not succeed:
            return False

        # 查找对应的提交
        target_hash = None

        def find_target_commit(set_process):
            nonlocal target_hash
            set_process(0)
            for i in range(len(std_out)):
                set_process(i / len(std_out))
                cur_line = std_out[i]
                m = re.match(r"^(\w+).*更新至.*?(\d+\.\d+\.\d+)", cur_line)
                if not m:
                    continue
                target_hash = m.group(1)
                break
            if target_hash is None:
                raise Exception("未找到目标版本提交")
            set_process(1)

        processTask.run_step("查找目标版本提交", find_target_commit)

        if target_hash is None:
            return False

        # 切换到目标提交
        succeed = processTask.run_cmd_task("切换到目标提交", self.config.rf_path,
                                           ["git", "reset", "--hard", target_hash])
        if not succeed:
            return False

        succeed = True
        # 检查版本
        try:
            cur_version = PackageState.get_rf_package_version(self.config.rf_path)
        except Exception:
            succeed = False

        succeed = succeed and cur_version == target_version
        if not succeed:
            utils.print_hint("[red]切换后的版本不匹配[/]")
