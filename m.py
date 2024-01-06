import random
from rich.panel import Panel
from rich import print
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
import time


allStr = []


def add():
    global allStr
    allStr.append(str(random.randint(0, 1000)))
    return getPanel(allStr)


def getPanel(strs):
    st = ""
    l = len(strs)
    start = l - 5

    for i in range(max(start, 0), l):
        st += strs[i]
        if i < l - 1:
            st += "\n"

    return Panel(st, height=7, title="Welcome")


with Live(add(), refresh_per_second=4) as live:
    for _ in range(40):
        time.sleep(0.4)
        live.update(add())
