MoveOutPackage = None

import processTask
from utils import Utils, Step
import json
from packageState import PackageState
from menuMgr import MenuMgr, KeyAction, Menu
from mainMenu import MainMenu
from program import Program

class MoveOutPackage:
    def addFrameworkChangeToGit(addPackagesLockAlso: bool = False) -> bool:
        Utils.printInline("添加项目内RenderFramework改动到Git: ")

        stderr = ""

        def exe(setProcess):
            setProcess(0.5)
            packagePath = Utils.getPackagePath(
                Program.getCurProjectPath(), False, PackageState.version
            )
            global stderr
            _, stderr = Utils.executeGitCommand(["add", packagePath + "/*"])

            if "error:" not in stderr and addPackagesLockAlso:
                packagesPath = Utils.getUnityPackagesPath(Program.getCurProjectPath())
                _, stderr = Utils.executeGitCommand(["add", packagesPath + "/packages-lock.json"])

            setProcess(1)

        processTask.run(exe)

        if "error:" not in stderr:
            print(Utils.color("成功", 32))
            return True
        else:
            print(Utils.color("失败: ", 31))
            print(stderr)
            return False


    def modifyPackageLockJson(setProcess):
        packagesLockJsonPath = Utils.getPackagesLockJsonPath(Program.getCurProjectPath())
        with open(packagesLockJsonPath) as f:
            packagesLockJson = json.load(f)

        setProcess(0.3)

        packageJson = packagesLockJson["dependencies"][Utils.PACKAGE_NAME]
        packageJson["source"] = "embedded"
        packageJson["version"] = "file:" + Utils.getPackageFullName(PackageState.version)
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
        def step0():
            try:
                src = Utils.getPackagePath(Program.getCurProjectPath(), True, PackageState.version)
                dest = Utils.getPackagePath(Program.getCurProjectPath(), False, PackageState.version)
                processTask.run(
                    lambda setProcess: Utils.copyDirectory(src, dest, True, setProcess)
                )
                return None
            except Exception as e:
                return str(e)

        if not Step("移出Package文件: ", step0).execute():
            MenuMgr.switchMenu(MainMenu.getMenu())
            return

        # 修改json ------------------------------------------
        def step1():
            try:
                processTask.run(MoveOutPackage.modifyPackageLockJson)
                return None
            except Exception as e:
                return str(e)

        if not Step("修改packages-lock.json配置: ", step1).execute():
            MenuMgr.switchMenu(MainMenu.getMenu())
            return

        # 将修改添加到git ------------------------------------------
        if not MoveOutPackage.addFrameworkChangeToGit(True):
            MenuMgr.switchMenu(MainMenu.getMenu())
            return

        # 提交 ------------------------------------------
        if commit:

            def step2():
                def commit(setProcess):
                    setProcess(0.5)
                    Utils.executeGitCommand(["commit", "-m", "feat：【RF】移出包体"])
                    setProcess(1)

                try:
                    processTask.run(commit)
                    return None
                except Exception as e:
                    return str(e)

            if not Step("提交修改到git: ", step2).execute():
                MenuMgr.switchMenu(MainMenu.getMenu())
                return

        print(Utils.color("移出完成", 32))
        MenuMgr.switchMenu(MainMenu.getMenu())


    def getMenu():
        return Menu(
            "是否提交修改？",
            [
                KeyAction("a", "不提交", MoveOutPackage.moveOutPackage),
                KeyAction("s", "提交", lambda: MoveOutPackage.moveOutPackage(True)),
                KeyAction("q", "返回", lambda: MenuMgr.switchMenu(MainMenu.getMenu())),
            ],
            1,
        )


    def trySwitchMoveOutPackageMenu():
        print()

        if not PackageState.inCache:
            print(Utils.color("Package不在Cache中，无需移出", 33))
            return

        if not PackageState.exists:
            print(Utils.color("Cache内不存在本地Package文件，无需移出，可以使用Unity重新下载", 33))
            return

        MenuMgr.switchMenu(MoveOutPackage.getMenu())
