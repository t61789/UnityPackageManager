import utils
import config
import program
import packageState
import menuMgr
import moveOutPackage
import modifyPackageVersion
import copyToRfProject
import clearAllModifies
import deleteShaderCache


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

    # BN Package版本
    s += "[BN_Package版本]\t" + utils.getPackageVersionStr(packageState.version, 33) + "\n"

    # RF Package版本
    if packageState.rfVersion == packageState.version:
        needBack = False
        needUpdate = False
    else:
        needBack = packageState.isVersionHigher(packageState.rfVersion, packageState.version)
        needUpdate = not needBack

    if needUpdate:
        versionNote = utils.color(" [需要更新]", 31)
    elif needBack:
        versionNote = utils.color(" [需要回退]", 31)
    else:
        versionNote = ""
    s += "[RF_Package版本]\t" + utils.getPackageVersionStr(packageState.rfVersion, 33) + versionNote + "\n"
    print(s)


menuMgr.registerMenu(
    menuMgr.MAIN_MENU,
    menuMgr.Menu(
        getMainMenuHeader,
        [
            menuMgr.KeyAction("w", "重新读取项目信息", None),
            menuMgr.KeyAction("v", "切换工程", program.switchProjectIndex),
            menuMgr.KeyAction("a", "移出Package", moveOutPackage.trySwitchMoveOutPackageMenu),
            menuMgr.KeyAction(
                "r", "修改Package版本", lambda: menuMgr.switchMenu(menuMgr.MODIFY_PACKAGE_JSON_MENU)
            ),
            menuMgr.KeyAction("g", "复制Package到RF工程", copyToRfProject.startCopy),
            menuMgr.KeyAction("s", "清除所有修改", clearAllModifies.clearAllModifies),
            menuMgr.KeyAction("b", "删除ShaderCache", deleteShaderCache.deleteShaderCache),
            menuMgr.KeyAction("q", "退出", utils.exitApplication),
            # TODO 进阶操作
        ],
    ),
)
