Config = None
ProjectPath = None

import json
from utils import *

class ProjectPath:
    def __init__(self, byname : str, path : str):
        self.byname = byname
        self.path = path

class Config:
    projectPaths = []
    rfPath = ""

    def loadConfig():
        try:
            with open(getConfigJsonPath()) as f:
                configJson = json.load(f)
        except Exception as e:
            raise Exception("读取config.json文件失败: " + str(e))

        Config.projectPaths.clear()
        try:
            projectPathsJson = configJson["projectPaths"]
            for i in range(len(projectPathsJson)):
                projectPathJson = projectPathsJson[i]
                projectPath = ProjectPath(None, None)
                projectPath.byname = projectPathJson["byname"]
                projectPath.path = projectPathJson["path"].replace('\\', '/')
                Config.projectPaths.append(projectPath)
            rfPath = configJson["renderFrameworkPath"].replace('\\', '/')
        except Exception as e:
            raise Exception("config.json格式错误")
        
        if(len(Config.projectPaths) == 0):
            raise Exception("无指定的工程")
        
        if(rfPath == None or rfPath == ""):
            raise Exception("RenderFramework未指定")
