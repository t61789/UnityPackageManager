import utils
import shutil
import os
import program


def getNeedDeleteFilesPath() -> ([str], [str]):
    bnPath = program.getCurProjectPath()
    shaderCacheDbPath = bnPath + "/Library/ShaderCache.db"
    shaderCachePath = bnPath + "/Library/ShaderCache"
    playerDataCache = bnPath + "/Library/PlayerDataCache"
    return ([shaderCacheDbPath], [shaderCachePath, playerDataCache])


def delete(path: str, isFile: bool) -> bool:
    utils.printInline("正在删除：" + os.path.relpath(path, program.getCurProjectPath()))
    try:
        if isFile:
            os.remove(path)
        else:
            shutil.rmtree(path)
    except Exception as e:
        print(utils.color(" 失败：", 31), e.args)
        return False

    print(utils.color(" 成功", 32))
    return True


def deleteShaderCache():
    print()

    (files, dirs) = getNeedDeleteFilesPath()

    for p in files:
        delete(p, True)
    for p in dirs:
        delete(p, False)

    print(utils.color("删除完成", 32))
