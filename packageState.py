import json
import os
import utils
import re
from config import Config


class PackageVersion:
    def __init__(self, unity_code: int, level_code: int, version_code: int):
        self.unity_code = unity_code
        self.level_code = level_code
        self.version_code = version_code
        
    @staticmethod
    def load_from_str(package_version: str):
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", package_version)
        if not match:
            return PackageVersion.get_unavailable()

        return PackageVersion(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    
    def __eq__(self, other):
        result = self.unity_code == other.unity_code
        result = result and self.level_code == other.level_code
        result = result and self.version_code == other.version_code
        return result
    
    def to_str(self, color: int = -1) -> str:
        color_prefix = "" if color < 0 else ("\x1b[" + str(color) + "m")
        color_post_fix = "" if color < 0 else "\x1b[0m"

        return str(self.unity_code) + "." + str(self.level_code) + "." + color_prefix + str(self.version_code) + color_post_fix

    @staticmethod
    def get_unavailable():
        return PackageVersion(-1, -1, -1)

    def is_higher(self, other):
        if self.unity_code > other.unity_code:
            return True
        if self.unity_code < other.unity_code:
            return False
        if self.level_code > other.level_code:
            return True
        if self.level_code < other.level_code:
            return False
        if self.version_code > other.version_code:
            return True
        return False


class PackageState:
    def __init__(self, cur_config: Config):
        self.in_cache = False
        self.path = ""
        self.exists = False
        self.version = PackageVersion.get_unavailable()
        self.rf_version = PackageVersion.get_unavailable()
        self.config = cur_config

    @staticmethod
    def __get_rf_package_version(rf_path: str) -> PackageVersion:
        package_json_path = os.path.join(rf_path, "package.json")
        with open(package_json_path) as f:
            package_json = json.load(f)
        return PackageVersion.load_from_str(package_json["version"])
    
    def analyze_package_state(self, project_path):
        # 读取packages-lock.json，判断包位置
        try:
            with open(utils.get_packages_lock_json_path(project_path)) as f:
                packages_lock_json = json.load(f)
        except Exception as e:
            raise Exception("读取packages-lock.json文件失败: " + str(e))

        try:
            self.in_cache = packages_lock_json["dependencies"][utils.PACKAGE_NAME]["source"] != "embedded"

            if self.in_cache:
                self.version = PackageVersion.load_from_str(packages_lock_json["dependencies"][utils.PACKAGE_NAME]["version"])
                self.path = utils.get_package_path(project_path, self.in_cache, self.version)
                self.exists = os.path.exists(utils.get_package_json_path(self.path))
        except Exception:
            raise Exception("packages-lock.json格式错误，建议使用Unity重新生成")

        if not self.in_cache:
            # 如果包不在Cache里，packages-lock.json中就不包含版本信息，需要去Packages文件夹下找可用的包
            available_package_dirs = PackageState.__find_available_package_directories(project_path, self.in_cache)
            if len(available_package_dirs) == 0:
                raise Exception("packages-lock.json描述包在Packages内，但未找到可用的包，请使用Unity重新生成")

            # 取最高版本的包
            max_version = PackageVersion(-1, -1, -1)
            max_version_dir = ""
            for dir_path, cur_version in available_package_dirs:
                if cur_version.is_higher(max_version):
                    max_version = cur_version
                    max_version_dir = dir_path

            self.version = max_version
            self.path = max_version_dir
            self.exists = True

        # 判断RF工程版本
        try:
            self.rf_version = PackageState.__get_rf_package_version(self.config.rf_path)
        except Exception:
            raise Exception("读取RF工程版本失败，请检查RF工程配置是否正确")

    @staticmethod
    def __find_available_package_directories(project_path: str, in_cache: bool) -> list:
        available_package_dirs = []
        finding_dir = utils.get_unity_package_cache_path(project_path) if in_cache else utils.get_unity_packages_path(project_path)

        for dir_name in os.listdir(finding_dir):
            dir_path = os.path.join(finding_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue
            if utils.PACKAGE_NAME not in dir_name:
                continue
            try:
                with open(os.path.join(dir_path, "package.json")) as f:
                    package_json = json.load(f)
                    version = PackageVersion.load_from_str(package_json["version"])
                    available_package_dirs.append((dir_path, version))
            except Exception:
                continue

        return available_package_dirs




