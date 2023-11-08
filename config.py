import json
import utils


class ProjectPath:
    def __init__(self, byname: str, path: str):
        self.byname = byname
        self.path = path


projectPaths = []
rfPath = ""
unityEditorPath = ""


def loadConfig():
    try:
        with open(utils.getConfigJsonPath()) as f:
            configJson = json.load(f)
    except Exception as e:
        raise Exception("读取config.json文件失败: " + str(e))

    global projectPaths, rfPath, unityEditorPath
    projectPaths.clear()
    try:
        projectPathsJson = configJson["projectPaths"]
        for i in range(len(projectPathsJson)):
            projectPathJson = projectPathsJson[i]
            projectPath = ProjectPath(None, None)
            projectPath.byname = projectPathJson["byname"]
            projectPath.path = projectPathJson["path"].replace("\\", "/")
            projectPaths.append(projectPath)
        rfPath = configJson["renderFrameworkPath"].replace("\\", "/")
        unityEditorPath = configJson["unityEditorPath"].replace("\\", "/")
    except Exception as e:
        raise Exception("config.json格式错误")

    if len(projectPaths) == 0:
        raise Exception("无指定的工程")

    if rfPath == None or rfPath == "":
        raise Exception("RenderFramework未指定")
