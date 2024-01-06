import termcursor
from rich.progress import *


class TimeElapsedColumnAdvance(ProgressColumn):
    """Renders time elapsed."""

    def render(self, task: "Task") -> Text:
        """Show time elapsed."""
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("-:--:--:--", style="progress.elapsed")
        delta = timedelta(seconds=max(0, elapsed))
        return Text(str(delta)[2:10:], style="progress.elapsed")


def run_step(name: str, action: Callable[[Callable[[float], None]], None]) -> bool:
    termcursor.hidecursor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumnAdvance(),
    ) as progress:
        step = progress.add_task(description=name, total=1)

        def update_progress(val):
            progress.update(step, completed=val)

        error_str = None
        try:
            action(update_progress)
        except Exception as e:
            error_str = str(e)

    termcursor.showcursor()

    if error_str is None or error_str == "":
        # print(utils.color(" 完成", 32))
        return True
    else:
        # print(utils.color(" 失败", 31))
        print(error_str)
        return False
