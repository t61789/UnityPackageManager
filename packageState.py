import json
import os
import utils

inCache = False
path = ""
exists = False
version = None

def analyzePackageState(projectPath):

    # 判断packages-lock.json中指明的package版本和位置
    packagesLockJsonPath = utils.getPackagesLockJsonPath(projectPath)

    if(not os.path.exists(packagesLockJsonPath)):
        raise Exception("找不到指定工程的packages-lock.json文件: " + packagesLockJsonPath)

    try:
        with open(packagesLockJsonPath) as f:
            packagesLockJson = json.load(f)
    except Exception as e:
        raise Exception("读取packages-lock.json文件失败: " + str(e))

    global inCache, path, exists, version
    try:
        inCache = packagesLockJson["dependencies"][utils.PACKAGE_NAME]["source"] != "embedded"
        version = utils.getPackageVersion(packagesLockJson["dependencies"][utils.PACKAGE_NAME]["version"])
    except Exception as e:
        raise Exception("packages-lock.json格式错误，建议使用Unity重新生成")

    path = utils.getPackagePath(projectPath, inCache, version)
    # 检查路径下的package是否可用
    # 需要package文件夹内的package.json存在
    exists = os.path.exists(utils.getPackageJsonPath(path))
