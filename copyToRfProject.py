import program
import utils
import processTask
import menuMgr
import config
import packageState


def copyTo():
    unityProjectPath = program.getCurProjectPath()
    rfPath = config.rfPath

    step = lambda setProcess: utils.clearDirectory(rfPath, setProcess)
    if not processTask.runStep("清空RF工程: ", step):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    step = lambda setProcess: utils.copyDirectory(
        utils.getPackagePath(unityProjectPath, False, packageState.version),
        rfPath,
        False,
        setProcess,
    )
    if not processTask.runStep("复制Package到RF工程: ", step):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    print(utils.color("复制成功", 32))


def startCopy():
    if packageState.inCache:
        print(utils.color("Package未移出，无法复制", 31))
        return

    if packageState.version != packageState.rfVersion:
        print()
        confirm = menuMgr.confirmMenu(utils.color("BN_Package版本与RF_Package版本不一致，是否继续？", 33))
        print()
        if not confirm:
            print(utils.color("取消操作", 31))
            return

    # TODO 检查RF工程git是否有修改, 用git status

    copyTo()
