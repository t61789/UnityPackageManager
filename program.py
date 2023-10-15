Program = None

from config import *
from packageState import *
from utils import *
from mainMenu import MainMenu
from menuMgr import *

class Program:
    curProjectIndex = 0

    def switchProjectIndex():
        Program.curProjectIndex = (Program.curProjectIndex + 1) % max(len(config.projectPaths), 1)
        print("开始切换到第" + str(Program.curProjectIndex) + "个工程")

    configError = Menu(
        SPLITER + "\n读取配置文件出错",
        [
            KeyAction("w", "重新读取配置文件", None),
            KeyAction("v", "切换工程", switchProjectIndex),
            KeyAction("q", "退出", exitApplication),
        ],
    )

    packageError = Menu(
        SPLITER + "\n读取项目信息出错",
        [
            KeyAction("w", "重新读取项目信息", None),
            KeyAction("v", "切换工程", switchProjectIndex),
            KeyAction("q", "退出", exitApplication),
        ],
    )

    def getCurProjectPath():
        return Config.projectPaths[Program.curProjectIndex].path

    def initializeTick():
        try:
            Config.loadConfig()
        except Exception as e:
            log("读取配置文件出错: " + str(e), LogType.Error)
            MenuMgr.switchMenu(Program.configError)

        try:
            PackageState.analyzePackageState(Program.getCurProjectPath())
        except Exception as e:
            log("分析项目结构出错：" + str(e), LogType.Error)
            MenuMgr.switchMenu(Program.packageError)

    def switchToMainMenu():
        MenuMgr.switchMenu(MainMenu.getMenu())