import subprocess
from rich.progress import *
import time
from rich.panel import Panel

cmd = ["git", "pull"]
cwd = "F:\\Unity\\UnityProjects\\Polaris_BN_Main\\UnityProj"
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, cwd=cwd, encoding="utf-8")

process.communicate()

print(process.returncode)

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
