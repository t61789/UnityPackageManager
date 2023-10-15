MainMenu = None

from config import Config
from moveOutPackage import *
from packageState import *
from program import *
from utils import *
from menuMgr import *

class MainMenu:
    def getCandidateProjects() -> str:
        projectNum = len(Config.projectPaths)
        if projectNum == 0:
            return None
        s = "[Unity项目候选]\t\t"
        for i in range(projectNum):
            byname = Config.projectPaths[i].byname
            if i == Program.curProjectIndex:
                byname = color(byname, 34)
            s += byname
            if i != projectNum - 1:
                s += " | "
        return s + "\n"

    def getMainMenuHeader() -> str:
        projectPath = Config.projectPaths[Program.curProjectIndex]
        s = "\n"

        s += SPLITER + "\n"

        # Unity项目候选
        s += MainMenu.getCandidateProjects()

        # Unity项目路径
        byname = color(projectPath.byname, 34)
        s += "[Unity项目路径]\t\t" + byname + " " + projectPath.path + "\n"

        # RenderFramework路径
        s += "[RenderFramework路径]\t" + Config.rfPath + "\n"

        # Package位置
        if PackageState.inCache:
            packagePosition = color("Cache", 32)
            if not PackageState.exists:
                packagePosition += color("（不存在本地文件）", 35)
        else:
            packagePosition = color("Packages", 31)

        s += "[Package位置]\t\t" + packagePosition + "\n"

        # Package版本
        s += "[Package版本]\t\t" + getPackageVersionStr(PackageState.version, 33) + "\n"
        print(s)


    def getMenu() -> Menu:
        return Menu(
            MainMenu.getMainMenuHeader,
            [
                KeyAction("w", "重新读取项目信息", None),
                KeyAction("v", "切换工程", Program.switchProjectIndex),
                KeyAction(
                    "a", "移出Package", MoveOutPackage.trySwitchMoveOutPackageMenu()
                ),
                KeyAction("q", "退出", exitApplication),
            ],
        )
