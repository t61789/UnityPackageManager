Program = None

from config import Config
from packageState import PackageState
from utils import Utils, LogType
from mainMenu import MainMenu
from menuMgr import MenuMgr, KeyAction, Menu


class Program:
    curProjectIndex = 0

    def switchProjectIndex():
        Program.curProjectIndex = (Program.curProjectIndex + 1) % max(
            len(Config.projectPaths), 1
        )
        print("开始切换到第" + str(Program.curProjectIndex) + "个工程")

    def getConfigErrorMenu():
        return Menu(
            Utils.SPLITER + "\n读取配置文件出错",
            [
                KeyAction("w", "重新读取配置文件", None),
                KeyAction("v", "切换工程", Program.switchProjectIndex),
                KeyAction("q", "退出", Utils.exitApplication),
            ],
        )

    def getPackageErrorMenu():
        return Menu(
            Utils.SPLITER + "\n读取项目信息出错",
            [
                KeyAction("w", "重新读取项目信息", None),
                KeyAction("v", "切换工程", Program.switchProjectIndex),
                KeyAction("q", "退出", Utils.exitApplication),
            ],
        )

    def getCurProjectPath():
        return Config.projectPaths[Program.curProjectIndex].path

    def initializeTick():
        try:
            Config.loadConfig()
        except Exception as e:
            Utils.log("读取配置文件出错: " + str(e), LogType.Error)
            MenuMgr.switchMenu(Program.getConfigErrorMenu())

        try:
            PackageState.analyzePackageState(Program.getCurProjectPath())
        except Exception as e:
            Utils.log("分析项目结构出错：" + str(e), LogType.Error)
            MenuMgr.switchMenu(Program.getPackageErrorMenu())

    def switchToMainMenu():
        MenuMgr.switchMenu(MainMenu.getMenu())
