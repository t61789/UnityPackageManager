from typing import Callable
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


def runStep(name: str, action: Callable[[Callable[[float], None]], None]) -> bool:
    termcursor.hidecursor()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumnAdvance(),
    ) as progress:
        step = progress.add_task(description=name, total=1)

        def updateProgress(val):
            progress.update(step, completed=val)

        errorStr = None
        try:
            action(updateProgress)
        except Exception as e:
            errorStr = str(e)

    termcursor.showcursor()

    if errorStr == None or errorStr == "":
        # print(utils.color(" 完成", 32))
        return True
    else:
        # print(utils.color(" 失败", 31))
        print(errorStr)
        return False
