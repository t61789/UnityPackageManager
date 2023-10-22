import packageState
import menuMgr
import utils
import config
import program

curProjectIndex = 0


def switchProjectIndex():
    global curProjectIndex
    curProjectIndex = (curProjectIndex + 1) % max(len(config.projectPaths), 1)
    print("开始切换到第" + str(curProjectIndex) + "个工程")


def getCurProjectPath():
    return config.projectPaths[curProjectIndex].path


def initializeTick():
    try:
        config.loadConfig()
    except Exception as e:
        utils.log("读取配置文件出错: " + str(e), utils.LogType.Error)
        menuMgr.switchMenu(menuMgr.CONFIG_ERROR_MENU)

    try:
        packageState.analyzePackageState(getCurProjectPath())
    except Exception as e:
        utils.log("分析项目结构出错：" + str(e), utils.LogType.Error)
        menuMgr.switchMenu(menuMgr.PACKAGE_ERROR_MENU)

def executeGitCommand(args: [str]):
    return utils.executeCmd(["git"] + args, program.getCurProjectPath())

menuMgr.registerMenu(
    menuMgr.CONFIG_ERROR_MENU,
    menuMgr.Menu(
        utils.SPLITER + "\n读取配置文件出错",
        [
            menuMgr.KeyAction("w", "重新读取配置文件", None),
            menuMgr.KeyAction("v", "切换工程", switchProjectIndex),
            menuMgr.KeyAction("q", "退出", utils.exitApplication),
        ],
    ),
)

menuMgr.registerMenu(
    menuMgr.PACKAGE_ERROR_MENU,
    menuMgr.Menu(
        utils.SPLITER + "\n读取项目信息出错",
        [
            menuMgr.KeyAction("w", "重新读取项目信息", None),
            menuMgr.KeyAction("v", "切换工程", switchProjectIndex),
            menuMgr.KeyAction("q", "退出", utils.exitApplication),
        ],
    ),
)
