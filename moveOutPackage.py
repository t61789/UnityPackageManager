import processTask
import utils
import json
import packageState
import menuMgr
import program


def addFrameworkChangeToGit(setProcess, addPackagesLockAlso: bool = False):
    setProcess(0.5)
    packagePath = utils.getPackagePath(program.getCurProjectPath(), False, packageState.version)
    _, stderr = program.executeGitCommand(["add", packagePath + "/*"])

    if "error: " in stderr:
        raise Exception(stderr)

    if addPackagesLockAlso:
        packagesPath = utils.getUnityPackagesPath(program.getCurProjectPath())
        _, stderr = program.executeGitCommand(["add", packagesPath + "/packages-lock.json"])

    setProcess(1)


def modifyPackageLockJson(setProcess):
    packagesLockJsonPath = utils.getPackagesLockJsonPath(program.getCurProjectPath())
    with open(packagesLockJsonPath) as f:
        packagesLockJson = json.load(f)

    setProcess(0.3)

    packageJson = packagesLockJson["dependencies"][utils.PACKAGE_NAME]
    packageJson["source"] = "embedded"
    packageJson["version"] = "file:" + utils.getPackageFullName(packageState.version)
    packageJson["depth"] = 0
    del packageJson["url"]

    setProcess(0.6)

    with open(packagesLockJsonPath, "w", newline="\n") as f:
        f.write(json.dumps(packagesLockJson, indent=2))
        f.write("\n")
        f.flush()

    setProcess(1)


def moveOutPackage(commit: bool = False):
    print()

    # 移出文件 ------------------------------------------
    def step0(setProcess):
        src = utils.getPackagePath(program.getCurProjectPath(), True, packageState.version)
        dest = utils.getPackagePath(program.getCurProjectPath(), False, packageState.version)
        utils.copyDirectory(src, dest, True, setProcess)
        return None

    if not processTask.runStep("移出Package文件: ", step0):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    # 修改json ------------------------------------------
    if not processTask.runStep("修改packages-lock.json配置: ", modifyPackageLockJson):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    # 将修改添加到git ------------------------------------------
    def step2(setProcess):
        addFrameworkChangeToGit(setProcess, True)

    if not processTask.runStep("将修改添加到git: ", step2):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    # 提交 ------------------------------------------
    if commit:

        def step3(setProcess):
            setProcess(0.5)
            _, stderr = program.executeGitCommand(["commit", "-m", "feat：【RF】移出包体"])
            if "error: " in stderr:
                raise Exception(stderr)
            setProcess(1)

        if not processTask.runStep("提交修改到git: ", step3):
            menuMgr.switchMenu(menuMgr.MAIN_MENU)
            return

    """
    # 重新生成项目文件 ------------------------------------------
    def step4(setProcess):
        setProcess(0.1)
        program.syncProjectFiles()
        setProcess(1)

    processTask.runStep("重新生成项目文件: ", step4)
    """

    print(utils.color("移出完成", 32))
    menuMgr.switchMenu(menuMgr.MAIN_MENU)


def trySwitchMoveOutPackageMenu():
    print()

    if not packageState.inCache:
        print(utils.color("Package不在Cache中，无需移出", 33))
        return

    if not packageState.exists:
        print(utils.color("Cache内不存在本地Package文件，无需移出，可以使用Unity重新下载", 33))
        return

    menuMgr.switchMenu(menuMgr.MOVE_OUT_PACKAGE_MENU)


menuMgr.registerMenu(
    menuMgr.MOVE_OUT_PACKAGE_MENU,
    menuMgr.Menu(
        "是否提交修改？",
        [
            menuMgr.KeyAction("a", "不提交", moveOutPackage),
            menuMgr.KeyAction("s", "提交", lambda: moveOutPackage(True)),
            menuMgr.KeyAction("q", "返回", lambda: menuMgr.switchMenu(menuMgr.MAIN_MENU)),
        ],
        0,
    ),
)
