PackageState = None

import json
import os
from utils import *

class PackageState:
    inCache = False
    path = ""
    exists = False
    version = PackageVersion.getUnavailable()

    def analyzePackageState(projectPath):

        # 判断packages-lock.json中指明的package版本和位置
        packagesLockJsonPath = getPackagesLockJsonPath(projectPath)

        if(not os.path.exists(packagesLockJsonPath)):
            raise Exception("找不到指定工程的packages-lock.json文件: " + packagesLockJsonPath)

        try:
            with open(packagesLockJsonPath) as f:
                packagesLockJson = json.load(f)
        except Exception as e:
            raise Exception("读取packages-lock.json文件失败: " + str(e))

        global inCache
        global version
        try:
            inCache = packagesLockJson["dependencies"][PACKAGE_NAME]["source"] != "embedded"
            version = getPackageVersion(packagesLockJson["dependencies"][PACKAGE_NAME]["version"])
        except Exception as e:
            raise Exception("packages-lock.json格式错误，建议使用Unity重新生成")

        global path
        path = getPackagePath(projectPath, inCache, version)
        # 检查路径下的package是否可用
        # 需要package文件夹内的package.json存在
        global exists
        exists = os.path.exists(getPackageJsonPath(path))
