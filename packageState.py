import json
import os
import utils
import config

inCache = False
path = ""
exists = False
version = utils.PackageVersion.getUnavailable()
rfVersion = utils.PackageVersion.getUnavailable()

def getPackageVersion(packagePath: str) -> utils.PackageVersion:
    packageJsonPath = os.path.join(packagePath, "package.json")
    with open(packageJsonPath) as f:
        packageJson = json.load(f)
    return utils.getPackageVersion(packageJson["version"])
    

def findAvailablePackageDirectories(projectPath: str, inCache: bool) -> list:
    availablePackageDirectories = []
    findDirectory = (
        utils.getUnityPackageCachePath(projectPath)
        if inCache
        else utils.getUnityPackagesPath(projectPath)
    )

    for dirName in os.listdir(findDirectory):
        dirPath = os.path.join(findDirectory, dirName)
        if not os.path.isdir(dirPath):
            continue
        if utils.PACKAGE_NAME not in dirName:
            continue
        try:
            with open(os.path.join(dirPath, "package.json")) as f:
                packageJson = json.load(f)
                version = utils.getPackageVersion(packageJson["version"])
                availablePackageDirectories.append((dirPath, version))
        except:
            continue

    return availablePackageDirectories


def isVersionHigher(
    version1: utils.PackageVersion, version2: utils.PackageVersion
) -> bool:
    if version1.unityCode > version2.unityCode:
        return True
    if version1.unityCode < version2.unityCode:
        return False
    if version1.levelCode > version2.levelCode:
        return True
    if version1.levelCode < version2.levelCode:
        return False
    if version1.versionCode > version2.versionCode:
        return True
    return False


def analyzePackageState(projectPath):
    # 读取packages-lock.json，判断包位置
    try:
        with open(utils.getPackagesLockJsonPath(projectPath)) as f:
            packagesLockJson = json.load(f)
    except Exception as e:
        raise Exception("读取packages-lock.json文件失败: " + str(e))

    global inCache, path, exists, version
    try:
        inCache = (
            packagesLockJson["dependencies"][utils.PACKAGE_NAME]["source"] != "embedded"
        )

        if inCache:
            version = utils.getPackageVersion(
                packagesLockJson["dependencies"][utils.PACKAGE_NAME]["version"]
            )
            path = utils.getPackagePath(projectPath, inCache, version)
            exists = os.path.exists(utils.getPackageJsonPath(path))
            return
    except Exception as e:
        raise Exception("packages-lock.json格式错误，建议使用Unity重新生成")

    # 如果包不在Cache里，packages-lock.json中就不包含版本信息，需要去Packages文件夹下找可用的包
    availablePackageDirectories = findAvailablePackageDirectories(projectPath, inCache)
    if len(availablePackageDirectories) == 0:
        raise Exception("packages-lock.json描述包在Packages内，但未找到可用的包，请使用Unity重新生成")

    # 取最高版本的包
    maxVersion = utils.PackageVersion(-1, -1, -1)
    maxVersionDirPath = ""
    for dirPath, curVersion in availablePackageDirectories:
        if isVersionHigher(curVersion, maxVersion):
            maxVersion = curVersion
            maxVersionDirPath = dirPath

    version = maxVersion
    path = maxVersionDirPath
    exists = True

    # 判断RF工程版本
    global rfVersion
    try:
        rfVersion = getPackageVersion(config.rfPath)
    except:
        raise Exception("读取RF工程版本失败，请检查RF工程配置是否正确")

