import subprocess
from rich.progress import *
import time
from rich.panel import Panel
import processTask

cmd = ["git", "pull", "--no-rebase"]
cwd = "F:\\Unity\\UnityProjects\\Polaris_BN_Main\\UnityProj"
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=cwd, encoding="utf-8")

processTask.execute_cmd(lambda x: print(x), lambda x: print(x), None, cmd, cwd)

# with Live(refresh_per_second=20, transient=True) as live:

#     def update_live(s):
#         p = Panel.fit(s, title="title", title_align="left")

#         live.update(p, refresh=True)

#     s = ""
#     for l in iter(process.stdout.readline, b""):
#         if l == "":
#             break
#         s += l
#         # update_live(l)

#     time.sleep(0.1)
