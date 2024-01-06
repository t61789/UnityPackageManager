import enum
import os
import re
import shutil
import subprocess
import sys

from packageState import PackageVersion


class LogType(enum.Enum):
    Log = (1,)
    Warning = (2,)
    Error = 3


PACKAGE_NAME = "com.baitian.polaris.renderframework"
SPLITER = "[-------------------------------------------------------------]"


def exit_application():
    sys.exit(0)


def execute_cmd(args: [str], cwd: str) -> [str, str]:
    c = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
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


def color(s: str, color_code: int or None) -> str:
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
    if color_code is None:
        return s
    return "\x1b[" + str(color_code) + "m" + s + "\x1b[0m"


def copy_directory(src: str, dst: str, delete_src: bool = False, set_process=None):
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
    for relative_dir in dirs:
        dir_path = os.path.join(dst, relative_dir)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        count += 1
        if set_process is not None:
            set_process(count / size)
    for file in files:
        shutil.copy(os.path.join(src, file), os.path.join(dst, file))
        count += 1
        if set_process is not None:
            set_process(count / size)

    if delete_src:
        shutil.rmtree(src)


def clear_directory(path: str, set_process):
    dirs = []
    files = []
    if not os.path.exists(path):
        return

    for element in os.listdir(path):
        if element == ".git":
            continue

        p = os.path.join(path, element)
        if os.path.isdir(p):
            dirs.append(p)
        else:
            files.append(p)

    size = len(dirs) + len(files)
    count = 0
    for file in files:
        os.remove(file)
        count += 1
        if set_process is not None:
            set_process(count / size)
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
        count += 1
        if set_process is not None:
            set_process(count / size)


def print_inline(char):
    print(char, end="", flush=True)


def get_intent(intent: int):
    intend_str = ""
    for i in range(intent):
        intend_str += "  "
    return intend_str


def log(message: str, t: LogType = LogType.Log):
    if t == LogType.Error:
        message = "[\x1b[41mERROR\x1b[0m]" + message
    print(message)


def get_unity_packages_path(project_path: str) -> str:
    return project_path + "/Packages"


def get_unity_package_cache_path(project_path: str) -> str:
    return project_path + "/Library/PackageCache"


def get_packages_lock_json_path(project_path: str) -> str:
    return get_unity_packages_path(project_path) + "/packages-lock.json"


def get_manifest_json_path(project_path: str) -> str:
    return get_unity_packages_path(project_path) + "/manifest.json"


def get_package_version(package_path: str) -> PackageVersion:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", package_path)
    if not match:
        return PackageVersion.get_unavailable()

    return PackageVersion(int(match.group(1)), int(match.group(2)), int(match.group(3)))


def get_package_full_name(package_version: PackageVersion) -> str:
    return PACKAGE_NAME + "@" + package_version.to_str()


def get_package_path(project_path: str, in_cache: bool, package_version: PackageVersion) -> str:
    if in_cache:
        return os.path.join(
            get_unity_package_cache_path(project_path),
            get_package_full_name(package_version),
        )
    else:
        return os.path.join(get_unity_packages_path(project_path), get_package_full_name(package_version))


def get_package_json_path(package_path: str) -> str:
    return package_path + "/package.json"


def get_config_json_path() -> str:
    return "./config.json"
