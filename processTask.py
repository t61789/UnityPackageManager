import termcursor
import queue
import subprocess
import threading
import time
import datetime

from rich import text
from rich.panel import Panel
from rich.progress import *
from termcursor import termcursor
from rich.console import Console

spinner = ["-", "=", "#", "="]
spinner_index = 0
start_time = time.perf_counter()
console = Console(highlight=False)
print = console.print


def complete_info(task_name: str, elapsed: float, succeed: bool, arrow=None):
    start_time_str = f"[cornflower_blue][{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-4]}][/]"
    success_str = "[green][成功][/green]" if succeed else "[red][失败][/]"
    cost_time = f"[cyan][COST:{elapsed:.2f}s][/]"
    result = f"{start_time_str}>{cost_time}{success_str} {task_name}"
    if arrow is not None:
        result += f" {arrow}{arrow}{arrow}"
    return result


class TimeElapsedColumnAdvance(ProgressColumn):
    """Renders time elapsed."""

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--:--", style="progress.elapsed")
        delta = timedelta(seconds=max(0, elapsed))
        return Text(str(delta)[2:10:], style="progress.elapsed")


def run_tasks(tasks, stop_when_failed=True):
    all_succeed = True
    for task in tasks:
        try:
            if not task():
                all_succeed = False
                if stop_when_failed:
                    return False
        except Exception:
            all_succeed = False
            if stop_when_failed:
                return False
    return all_succeed


def run_step(name: str, action, raise_exception=False) -> bool:
    termcursor.hidecursor()
    global start_time
    start_time = time.perf_counter()

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumnAdvance(),
            transient=True
    ) as progress:
        step = progress.add_task(description=name, total=1)

        def update_progress(val):
            progress.update(step, completed=val)

        error_str = None
        try:
            action(update_progress)
        except Exception as e:
            if raise_exception:
                raise e
            error_str = str(e)

    termcursor.showcursor()

    if error_str is None or error_str == "":
        print(complete_info(name, time.perf_counter() - start_time, True))
        return True
    else:
        print(complete_info(name, time.perf_counter() - start_time, False))
        print(error_str)
        return False


def execute_cmd_simple(cmd: [str], cwd: str, remove_end=True):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=cwd,
                               encoding="utf-8", errors="ignore")
    stdout, stderr = process.communicate()
    if remove_end:
        if stdout and stdout.endswith("\n"):
            stdout = stdout[:-1]
        if stderr and stderr.endswith("\n"):
            stderr = stderr[:-1]
    return process.returncode == 0, stdout, stderr


def run_simple_cmd_tasks(tasks, stop_when_failed=True):
    all_succeed = True
    outputs = []
    for task in tasks:
        try:
            succeed, stdout, stderr = task()
            if not succeed:
                stdout = None
                all_succeed = False
                if stop_when_failed:
                    return False
            outputs.append((succeed, stdout, stderr))
        except Exception:
            all_succeed = False
            if stop_when_failed:
                return False
    return all_succeed


def execute_cmd(on_stdout: callable, on_stderr: callable, on_loop_start: callable, cmd: [str], cwd: str, shell=False):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=cwd,
                               encoding="utf-8", errors="ignore", shell=shell)

    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()

    def read_stream(stream, q):
        for l in iter(stream.readline, b""):
            if l == "":
                break
            q.put(l)

    thread_stdout = threading.Thread(target=read_stream, args=(process.stdout, stdout_queue))
    thread_stderr = threading.Thread(target=read_stream, args=(process.stderr, stderr_queue))
    thread_stdout.start()
    thread_stderr.start()

    leave = False
    while True:
        time.sleep(0.05)
        if on_loop_start:
            on_loop_start()
        while not stdout_queue.empty():
            line = stdout_queue.get()
            on_stdout(line)
        while not stderr_queue.empty():
            line = stderr_queue.get()
            on_stderr(line)

        if leave:
            break
        if process.poll() is not None:
            # 最后再读一次
            leave = True

    thread_stdout.join()
    thread_stderr.join()

    return process.returncode == 0


def run_cmd_read(cmd, work_space):
    stdout = []
    stderr = []
    execute_cmd(lambda x: stdout.append(x), lambda x: stderr.append(x), None, cmd, work_space)
    return stdout, stderr


def get_running_time():
    elapsed = time.perf_counter() - start_time
    return f"[[cyan]{spinner[spinner_index]} RUNNING {elapsed:.2f}s[/]]"


def get_executing_title(task_name: str, cmd: [str]):
    cmd_str = " ".join(cmd)
    return f"{task_name} {get_running_time()} [yellow]Execute Command: [/][green]{cmd_str}[/]"


def get_execute_error_title(task_name: str, cmd: [str]):
    cmd_str = " ".join(cmd)
    return f"[red]{task_name} {get_running_time()} Execute Command Error: {cmd_str}[/]"


def run_cmd_task(task_name: str, work_space: str, cmd: [str], show_detail_when_error: bool = True, stay_time=0.2,
                 stdout_list=None, stderr_list=None, shell=False):
    termcursor.hidecursor()

    output_list = []
    cmd_str = " ".join(cmd)
    output_list.append(f"执行：{cmd_str}\n")
    err_list = []
    buffer_max_size = 7

    global start_time
    start_time = time.perf_counter()

    def join_outputs(outputs):
        s = "".join(outputs)
        if s.endswith("\n"):
            s = s[:-1]
        return s

    with Live(refresh_per_second=20, transient=True) as live:

        def update_live():
            global spinner_index
            spinner_index = (spinner_index + 1) % len(spinner)
            p = Panel.fit(join_outputs(output_list), title=get_executing_title(task_name, cmd), title_align="left")

            live.update(p, refresh=True)

        def add_stderr(line):
            err_list.append(line)
            add_stdout(line)

        def add_stdout(line):
            output_list.append(line)
            if len(output_list) > buffer_max_size:
                output_list.pop(0)
            if stdout_list is not None:
                stdout_list.append(line)

        try:
            execute_success = execute_cmd(add_stdout, add_stderr, update_live, cmd, work_space, shell)
        except Exception as e:
            execute_success = False
        time.sleep(stay_time)

    has_err = len(err_list) > 0
    if not execute_success and has_err and show_detail_when_error:
        print(Panel.fit(join_outputs(err_list), title=get_execute_error_title(task_name, cmd), title_align="left"))

    if stderr_list is not None:
        stderr_list.extend(err_list)

    arrow = "^" if not execute_success and has_err else None
    print(complete_info(task_name, time.perf_counter() - start_time, execute_success, arrow))

    termcursor.showcursor()

    return execute_success

# success, elapsed_time = run_cmd_task("ping测试", ".", ["ping", "www.baidu.com"], show_detail_when_error=True)
# print(complete_info("ping测试", elapsed_time, success))
