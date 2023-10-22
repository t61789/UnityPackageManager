import enum
import os
import re
import shutil
import subprocess
import sys
from typing import Callable

class LogType(enum.Enum):
    Log = (1,)
    Warning = (2,)
    Error = 3


class PackageVersion:
    def __init__(self, unityCode: int, levelCode: int, versionCode: int):
        self.unityCode = unityCode
        self.levelCode = levelCode
        self.versionCode = versionCode

    def getUnavailable():
        return PackageVersion(-1, -1, -1)

PACKAGE_NAME = "com.unity.burst"
SPLITER = "[-------------------------------------------------------------]"

def exitApplication():
    sys.exit(0)

def executeCmd(args: [str], cwd: str) -> [str, str]:
    c = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
    )
    # c = subprocess.Popen(["git", "show"], stdout = subprocess.PIPE, cwd="D:\\UnityProjects\\PJGRASS")

    stdout = ""
    stderr = ""
    while c.poll() is None:
        while True:
            line = c.stdout.readline()
            if not line:
                break
            stdout += line.decode("utf-8").strip() + "\n"
        while True:
            line = c.stderr.readline()
            if not line:
                break
            stderr += line.decode("utf-8").strip() + "\n"
    c.wait()

    return stdout, stderr

def color(s: str, colorCode: int or None) -> str:
    # 字体颜色
    # 30:黑
    # 31:红
    # 32:绿
    # 33:黄
    # 34:蓝色
    # 35:紫色
    # 36:深绿
    # 37:白色

    # 背景颜色
    # 40:黑
    # 41:深红
    # 42:绿
    # 43:黄色
    # 44:蓝色
    # 45:紫色
    # 46:深绿
    # 47:白色
    if colorCode is None:
        return s
    return "\x1b[" + str(colorCode) + "m" + s + "\x1b[0m"

def copyDirectory(src: str, dst: str, deleteSrc: bool = False, setProcess=None):
    dirs = []
    files = []
    for path, dirNames, fileNames in os.walk(src):
        path = os.path.relpath(path, src)
        for dirName in dirNames:
            dirs.append(os.path.join(path, dirName))
        for fileName in fileNames:
            files.append(os.path.join(path, fileName))

    size = len(dirs) + len(files)
    count = 0
    for dir in dirs:
        dirPath = os.path.join(dst, dir)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
        count += 1
        if setProcess is not None:
            setProcess(count / size)
    for file in files:
        shutil.copy(os.path.join(src, file), os.path.join(dst, file))
        count += 1
        if setProcess is not None:
            setProcess(count / size)

    if deleteSrc:
        shutil.rmtree(src)

def printInline(char):
    print(char, end="", flush=True)

def log(message: str, type: LogType = LogType.Log):
    if type == LogType.Error:
        message = "[\x1b[41mERROR\x1b[0m]" + message
    print(message)

def getUnityPackagesPath(projectPath: str) -> str:
    return projectPath + "/Packages"

def getUnityPackageCachePath(projectPath: str) -> str:
    return projectPath + "/Library/PackageCache"

def getPackagesLockJsonPath(projectPath: str) -> str:
    return getUnityPackagesPath(projectPath) + "/packages-lock.json"

def getPackageVersionStr(packageVersion: PackageVersion, color: int = -1) -> str:
    colorPrefix = "" if color < 0 else ("\x1b[" + str(color) + "m")
    colorPostFix = "" if color < 0 else "\x1b[0m"

    return (
        str(packageVersion.unityCode)
        + "."
        + str(packageVersion.levelCode)
        + "."
        + colorPrefix
        + str(packageVersion.versionCode)
        + colorPostFix
    )

def getPackageVersion(packagePath: str) -> PackageVersion:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", packagePath)
    if not match:
        return PackageVersion.getUnavailable()

    return PackageVersion(
        int(match.group(1)), int(match.group(2)), int(match.group(3))
    )

def getPackageFullName(packageVersion: PackageVersion) -> str:
    return PACKAGE_NAME + "@" + getPackageVersionStr(packageVersion)

def getPackagePath(
    projectPath: str, inCache: bool, packageVersion: PackageVersion
) -> str:
    if inCache:
        return os.path.join(
            getUnityPackageCachePath(projectPath),
            getPackageFullName(packageVersion),
        )
    else:
        return os.path.join(
            getUnityPackagesPath(projectPath), getPackageFullName(packageVersion)
        )

def getPackageJsonPath(packagePath: str) -> str:
    return packagePath + "/package.json"

def getConfigJsonPath() -> str:
    return "./config.json"

