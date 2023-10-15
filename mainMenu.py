MainMenu = None

from config import Config
from moveOutPackage import MoveOutPackage
from packageState import PackageState
from program import Program
from utils import Utils
from menuMgr import MenuMgr, KeyAction, Menu


class MainMenu:
    def getCandidateProjects() -> str:
        projectNum = len(Config.projectPaths)
        if projectNum == 0:
            return None
        s = "[Unity项目候选]\t\t"
        for i in range(projectNum):
            byname = Config.projectPaths[i].byname
            if i == Program.curProjectIndex:
                byname = Utils.color(byname, 34)
            s += byname
            if i != projectNum - 1:
                s += " | "
        return s + "\n"

    def getMainMenuHeader() -> str:
        projectPath = Config.projectPaths[Program.curProjectIndex]
        s = "\n"

        s += Utils.SPLITER + "\n"

        # Unity项目候选
        s += MainMenu.getCandidateProjects()

        # Unity项目路径
        byname = Utils.color(projectPath.byname, 34)
        s += "[Unity项目路径]\t\t" + byname + " " + projectPath.path + "\n"

        # RenderFramework路径
        s += "[RenderFramework路径]\t" + Config.rfPath + "\n"

        # Package位置
        if PackageState.inCache:
            packagePosition = Utils.color("Cache", 32)
            if not PackageState.exists:
                packagePosition += Utils.color("（不存在本地文件）", 35)
        else:
            packagePosition = Utils.color("Packages", 31)

        s += "[Package位置]\t\t" + packagePosition + "\n"

        # Package版本
        s += "[Package版本]\t\t" + Utils.getPackageVersionStr(PackageState.version, 33) + "\n"
        print(s)

    def getMenu() -> Menu:
        return Menu(
            MainMenu.getMainMenuHeader,
            [
                KeyAction("w", "重新读取项目信息", None),
                KeyAction("v", "切换工程", Program.switchProjectIndex),
                KeyAction("a", "移出Package", MoveOutPackage.trySwitchMoveOutPackageMenu),
                KeyAction("q", "退出", Utils.exitApplication),
            ],
        )
