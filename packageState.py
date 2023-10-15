PackageState = None

import json
import os
from utils import Utils, PackageVersion

class PackageState:
    inCache = False
    path = ""
    exists = False
    version = None

    def analyzePackageState(projectPath):

        # 判断packages-lock.json中指明的package版本和位置
        packagesLockJsonPath = Utils.getPackagesLockJsonPath(projectPath)

        if(not os.path.exists(packagesLockJsonPath)):
            raise Exception("找不到指定工程的packages-lock.json文件: " + packagesLockJsonPath)

        try:
            with open(packagesLockJsonPath) as f:
                packagesLockJson = json.load(f)
        except Exception as e:
            raise Exception("读取packages-lock.json文件失败: " + str(e))

        try:
            PackageState.inCache = packagesLockJson["dependencies"][Utils.PACKAGE_NAME]["source"] != "embedded"
            PackageState.version = Utils.getPackageVersion(packagesLockJson["dependencies"][Utils.PACKAGE_NAME]["version"])
        except Exception as e:
            raise Exception("packages-lock.json格式错误，建议使用Unity重新生成")

        PackageState.path = Utils.getPackagePath(projectPath, PackageState.inCache, PackageState.version)
        # 检查路径下的package是否可用
        # 需要package文件夹内的package.json存在
        PackageState.exists = os.path.exists(Utils.getPackageJsonPath(PackageState.path))
