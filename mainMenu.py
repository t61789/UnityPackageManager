import utils
import config
import program
import packageState
import menuMgr
import moveOutPackage


def getCandidateProjects() -> str:
    projectNum = len(config.projectPaths)
    if projectNum == 0:
        return None
    s = "[Unity项目候选]\t\t"
    for i in range(projectNum):
        byname = config.projectPaths[i].byname
        if i == program.curProjectIndex:
            byname = utils.color(byname, 34)
        s += byname
        if i != projectNum - 1:
            s += " | "
    return s + "\n"


def getMainMenuHeader() -> str:
    projectPath = config.projectPaths[program.curProjectIndex]
    s = "\n"

    s += utils.SPLITER + "\n"

    # Unity项目候选
    s += getCandidateProjects()

    # Unity项目路径
    byname = utils.color(projectPath.byname, 34)
    s += "[Unity项目路径]\t\t" + byname + " " + projectPath.path + "\n"

    # RenderFramework路径
    s += "[RenderFramework路径]\t" + config.rfPath + "\n"

    # Package位置
    if packageState.inCache:
        packagePosition = utils.color("Cache", 32)
        if not packageState.exists:
            packagePosition += utils.color("（不存在本地文件）", 35)
    else:
        packagePosition = utils.color("Packages", 31)

    s += "[Package位置]\t\t" + packagePosition + "\n"

    # Package版本
    s += "[Package版本]\t\t" + utils.getPackageVersionStr(packageState.version, 33) + "\n"
    print(s)


menuMgr.registerMenu(
    menuMgr.MAIN_MENU,
    menuMgr.Menu(
        getMainMenuHeader,
        [
            menuMgr.KeyAction("w", "重新读取项目信息", None),
            menuMgr.KeyAction("v", "切换工程", program.switchProjectIndex),
            menuMgr.KeyAction("a", "移出Package", moveOutPackage.trySwitchMoveOutPackageMenu),
            menuMgr.KeyAction("q", "退出", utils.exitApplication),
        ],
    ),
)
