import re

import rich

import processTask
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
    def update_to_latest(work_space: str):
        def task0():
            return processTask.run_cmd_task("获取更新", work_space, ["git", "fetch"])

        def task1():
            return processTask.run_cmd_task("拉取更新", work_space, ["git", "pull", "--no-rebase"])

        return processTask.run_tasks([task0, task1])

    @staticmethod
    def remove_all_modifies(work_space: str):
        def task0():
            return processTask.run_cmd_task("添加所有修改", work_space, ["git", "add", "."], show_detail_when_error=True)

        def task1():
            return processTask.run_cmd_task("重置所有修改", work_space, ["git", "reset", "--hard", "head"], show_detail_when_error=True)

        return processTask.run_tasks([task0, task1])

    @staticmethod
    def get_need_push_commits_num(work_space: str):
        std_out = []
        std_err = []
        succeed = processTask.run_cmd_task(
            "获取需要推送的提交数量", work_space, ["git", "rev-list", "--count", "@{upstream}.."], stdout_list=std_out, stderr_list=std_err
        )
        if not succeed or len(std_out) == 0:
            return -1
        return int(std_out[0])

    @staticmethod
    def has_un_commit_changes(work_space: str):
        std_out = []
        std_err = []
        succeed = processTask.run_cmd_task("获取未提交的修改", work_space, ["git", "status", "-s"], stdout_list=std_out, stderr_list=std_err)
        if not succeed:
            return True
        return len(std_out) != 0

    def remove_modifies_and_update_to_latest(self):
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
        succeed = processTask.run_cmd_task("切换到目标提交", self.config.rf_path, ["git", "reset", "--hard", target_hash])
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
            print("[red]切换后的版本不匹配[/]")
