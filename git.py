import datetime

import termcursor
import queue
import subprocess
import threading
import time

from rich.panel import Panel
from rich.progress import *
from termcursor import termcursor

# spinner = ["|", "/", "-", "\\"]
spinner = ["-", "=", "#", "="]
spinner_index = 0
start_time = time.perf_counter()
console = Console(highlight=False)
print = console.print


def execute_cmd(on_stdout: callable, on_stderr: callable, on_loop_start: callable, cmd: [str], cwd: str):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
                               universal_newlines=True, cwd=cwd)

    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()

    def read_stream(stream, q):
        for l in iter(stream.readline, b''):
            if l == "":
                break
            q.put(l)

    thread_stdout = threading.Thread(target=read_stream, args=(process.stdout, stdout_queue))
    thread_stderr = threading.Thread(target=read_stream, args=(process.stderr, stderr_queue))
    thread_stdout.start()
    thread_stderr.start()

    leave = False
    while True:
        time.sleep(0.1)
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


def get_running_time():
    elapsed = time.perf_counter() - start_time
    return f"[[cyan]{spinner[spinner_index]} RUNNING {elapsed:.2f}s[/]]"


def get_executing_title(task_name: str, cmd: [str]):
    cmd_str = " ".join(cmd)
    return f"{task_name} {get_running_time()} [yellow]Execute Command: [/][green]{cmd_str}[/]"


def get_execute_error_title(task_name: str, cmd: [str]):
    cmd_str = " ".join(cmd)
    return f"[red]{task_name} {get_running_time()} Execute Command Error: {cmd_str}[/]"


def run_cmd_task(task_name: str, work_space: str, cmd: [str], show_detail_when_error: bool = False):
    termcursor.hidecursor()

    output_list = []
    err_list = []
    buffer_max_size = 7

    global start_time
    start_time = time.perf_counter()

    with Live(refresh_per_second=10, transient=True) as live:

        def update_live():
            global spinner_index
            spinner_index = (spinner_index + 1) % len(spinner)
            inner_s = "".join(output_list)
            p = Panel.fit(inner_s, title=get_executing_title(task_name, cmd), title_align="left",
                          height=len(output_list) + 2)

            live.update(p, refresh=True)

        def add_stderr(line):
            err_list.append(line)
            add_stdout(line)

        def add_stdout(line):
            output_list.append(line)
            if len(output_list) > buffer_max_size:
                output_list.pop(0)

        execute_cmd(add_stdout, add_stderr, update_live, cmd, work_space)
        time.sleep(3)

    has_err = len(err_list) > 0
    if has_err and show_detail_when_error:
        height = min(len(err_list) + 2, 100)
        print(
            Panel("".join(err_list), title=get_execute_error_title(task_name, cmd), title_align="left", height=height))

    termcursor.showcursor()

    return not has_err, time.perf_counter() - start_time


def complete_info(task_name: str, elapsed: float, succeed: bool):
    start_time_str = f"[cornflower_blue][{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-4]}][/]"
    success_str = "[green][成功][/green]" if succeed else "[red][失败][/]"
    cost_time = f"[cyan][COST:{elapsed:.2f}s][/]"
    return f"{start_time_str} {task_name} {success_str}{cost_time}"


success, elapsed_time = run_cmd_task("ping测试", "D:\\UnityProjects\\PJGRASS", ["git", "reset", "--hard", "head"], show_detail_when_error=True)
# print(complete_info("ping测试", elapsed_time, success))
