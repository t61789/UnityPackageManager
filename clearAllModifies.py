import menuMgr
import program
import processTask
import utils


def clearAllModifies():
    print()

    if not menuMgr.confirmMenu("确认要移除所有的修改吗？"):
        print(utils.color("取消操作", 31))
        return

    def step0(setProcess):
        setProcess(0.5)
        program.executeGitCommand(["add", "."])
        setProcess(1)

    if not processTask.runStep("添加所有修改: ", step0):
        return

    def step1(setProcess):
        setProcess(0.3)
        program.executeGitCommand(["reset", "--hard", "head"])
        setProcess(1)

    if not processTask.runStep("移除所有修改: ", step1):
        return

    print(utils.color("移除所有修改成功", 32))
