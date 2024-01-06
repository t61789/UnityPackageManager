import json
import utils


class ProjectPath:
    def __init__(self, byname: str, path: str):
        self.byname = byname
        self.path = path


class Config:
    def __init__(self):
        self.project_paths = []
        self.rf_path = ""
        self.unity_editor_path = ""

    def load_config(self):
        try:
            with open(utils.get_config_json_path()) as f:
                config_json = json.load(f)
        except Exception as e:
            raise Exception("读取config.json文件失败: " + str(e))

        self.project_paths.clear()
        try:
            project_paths_json = config_json["projectPaths"]
            for i in range(len(project_paths_json)):
                project_path_json = project_paths_json[i]
                project_path = ProjectPath("", "")
                project_path.byname = project_path_json["byname"]
                project_path.path = project_path_json["path"].replace("\\", "/")
                self.project_paths.append(project_path)
            rf_path = config_json["renderFrameworkPath"].replace("\\", "/")
            self.unity_editor_path = config_json["unityEditorPath"].replace("\\", "/")
        except Exception as e:
            raise Exception("config.json格式错误")

        if len(self.project_paths) == 0:
            raise Exception("无指定的工程")

        if rf_path is None or rf_path == "":
            raise Exception("RenderFramework未指定")
