import json
import menuMgr
import packageState
import utils
import readchar
import program
import processTask
import os
import config


def inputVersion(preVersion: utils.PackageVersion) -> utils.PackageVersion or None:
    print()
    versionStr = utils.getPackageVersionStr(preVersion)
    lastDotIndex = versionStr.rfind(".")
    versionStr = versionStr[0 : lastDotIndex + 1]
    utils.printInline("新的版本号：" + versionStr)

    inputStr = ""
    while True:
        k = readchar.readkey()
        if k == readchar.key.ESC:
            print(utils.color("\n取消输入", 31))
            return None
        if k == readchar.key.ENTER:
            print()
            print()
            break
        if k == readchar.key.BACKSPACE:
            if len(inputStr) > 0:
                inputStr = inputStr[:-1]
                utils.printInline("\x1b[1D \x1b[1D")
        else:
            utils.printInline(utils.color(k, 33))
            inputStr += k

    try:
        newVersionCode = int(inputStr)
        if newVersionCode <= 0:
            raise Exception()
    except:
        print(utils.color("\n无效输入", 31))
        return None

    return utils.getPackageVersion(versionStr + str(newVersionCode))


def modifyPackagesLockJson(packageVersion, setProcess):
    setProcess(0.5)

    projectPath = program.getCurProjectPath()
    packagesLockJsonPath = utils.getPackagesLockJsonPath(projectPath)
    with open(packagesLockJsonPath, "r") as f:
        packageJson = json.load(f)
    p = packageJson["dependencies"][utils.PACKAGE_NAME]
    p["version"] = utils.getPackageVersionStr(packageVersion)
    with open(packagesLockJsonPath, "w", newline="\n") as f:
        f.write(json.dumps(packageJson, indent=2))
        f.write("\n")
        f.flush()

    setProcess(1)


def modifyManifestJson(packageVersion, setProcess):
    setProcess(0.5)

    projectPath = program.getCurProjectPath()
    manifestJsonPath = utils.getManifestJsonPath(projectPath)
    with open(manifestJsonPath, "r") as f:
        manifestJson = json.load(f)
    d = manifestJson["dependencies"]
    d[utils.PACKAGE_NAME] = utils.getPackageVersionStr(packageVersion)
    with open(manifestJsonPath, "w", newline="\r\n") as f:
        f.write(json.dumps(manifestJson, indent=2))
        f.flush()

    setProcess(1)


def addJsonChangeToGit(setProcess):
    setProcess(0.3)

    program.executeGitCommand(
        [
            "add",
            program.getCurProjectPath() + "/Packages/manifest.json",
        ]
    )

    setProcess(0.6)

    program.executeGitCommand(
        [
            "add",
            program.getCurProjectPath() + "/Packages/packages-lock.json",
        ]
    )

    setProcess(1)


def commitChange(newVersion, setProcess):
    setProcess(0.5)

    program.executeGitCommand(
        [
            "commit",
            "-m",
            "feat：【renderframework】更新至" + utils.getPackageVersionStr(newVersion),
        ]
    )

    setProcess(1)


def modifyPackageInUnity():
    print()

    if not packageState.inCache:
        print(utils.color("包不在Cache中，无法修改", 31))
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    newVersion = inputVersion(packageState.version)
    if not newVersion:
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    if not processTask.runStep(
        "修改packages-lock.json配置: ",
        lambda setProcess: modifyPackagesLockJson(newVersion, setProcess),
    ):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    if not processTask.runStep(
        "修改manifest.json配置: ",
        lambda setProcess: modifyManifestJson(newVersion, setProcess),
    ):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    if not processTask.runStep("将修改添加到git: ", lambda setProcess: addJsonChangeToGit(setProcess)):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    if not processTask.runStep("提交修改: ", lambda setProcess: commitChange(newVersion, setProcess)):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    print(utils.color("修改成功", 32))
    menuMgr.switchMenu(menuMgr.MAIN_MENU)


def modifyPackagesJson(newVersion, setProcess):
    setProcess(0.3)

    packageJsonPath = config.rfPath + "/package.json"
    with open(packageJsonPath, "r") as f:
        packageJson = json.load(f)
    packageJson["version"] = utils.getPackageVersionStr(newVersion)
    with open(packageJsonPath, "w", newline="\r\n") as f:
        f.write(json.dumps(packageJson, indent=2))
        f.flush()

    setProcess(1)


def modifyPackageInRf():
    print()

    newVersion = inputVersion(packageState.rfVersion)
    if not newVersion:
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return
    if newVersion == packageState.rfVersion:
        print(utils.color("版本号未改变，取消操作", 31))
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    if not processTask.runStep(
        "修改packages.json配置: ", lambda setProcess: modifyPackagesJson(newVersion, setProcess)
    ):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    def commitPackageJsonChange(newVersion, setProcess):
        setProcess(0.1)
        program.executeGitCommandRf(["add", config.rfPath + "/package.json"])
        setProcess(0.6)
        program.executeGitCommandRf(
            [
                "commit",
                "-m",
                "feat：【版本】更新至" + utils.getPackageVersionStr(newVersion),
            ]
        )
        setProcess(1)

    if not processTask.runStep("提交修改: ", lambda setProcess: commitPackageJsonChange(newVersion, setProcess)):
        menuMgr.switchMenu(menuMgr.MAIN_MENU)
        return

    print(utils.color("修改成功", 32))
    menuMgr.switchMenu(menuMgr.MAIN_MENU)
    return


menuMgr.registerMenu(
    menuMgr.MODIFY_PACKAGE_JSON_MENU,
    menuMgr.Menu(
        "选择要修改的包",
        [
            menuMgr.KeyAction("r", "RF工程", modifyPackageInRf),
            menuMgr.KeyAction("e", "Unity工程", modifyPackageInUnity),
            menuMgr.KeyAction("q", "返回", lambda: menuMgr.switchMenu(menuMgr.MAIN_MENU)),
        ],
        newLine=True,
    ),
)
