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
        self.package_name = ""
        self.show_window_shortcut = []

    def load_config(self):
        try:
            with open(utils.get_config_json_path()) as f:
                config_json = json.load(f)
        except Exception as e:
            raise Exception("读取config.json文件失败: " + str(e))

        self.project_paths.clear()
        try:
            project_paths_json = config_json["project_paths"]
            for i in range(len(project_paths_json)):
                project_path_json = project_paths_json[i]
                project_path = ProjectPath("", "")
                project_path.byname = project_path_json["byname"]
                project_path.path = project_path_json["path"].replace("\\", "/")
                self.project_paths.append(project_path)
            self.rf_path = config_json["render_framework_path"].replace("\\", "/")
            self.unity_editor_path = config_json["unity_editor_path"].replace("\\", "/")
            self.package_name = config_json["package_name"]
            self.show_window_shortcut = config_json["show_window_shortcut"]
        except Exception:
            raise Exception("config.json格式错误")

        if len(self.project_paths) == 0:
            raise Exception("无指定的工程")

        if self.rf_path is None or self.rf_path == "":
            raise Exception("RenderFramework未指定")
