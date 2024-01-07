import utils
import shutil
import os
import processTask

from runtime import Runtime


class DeleteShaderCache:
    
    def __init__(self, runtime: Runtime):
        self.runtime = runtime

    def __get_need_delete_files_path(self) -> ([str], [str]):
        bn_path = self.runtime.get_cur_project_path()
        shader_cache_db_path = bn_path + "/Library/ShaderCache.db"
        shader_cache_path = bn_path + "/Library/ShaderCache"
        player_data_cache = bn_path + "/Library/PlayerDataCache"
        return [shader_cache_db_path], [shader_cache_path, player_data_cache]

    def __delete(self, path: str, is_file: bool) -> bool:
        def delete_target(set_process):
            set_process(0.5)
            if is_file:
                os.remove(path)
            else:
                shutil.rmtree(path)
            set_process(1)
        title = "删除：" + os.path.relpath(path, self.runtime.get_cur_project_path())
        return processTask.run_step(title, delete_target)
    
    def delete_shader_cache(self):
        print()

        (files, dirs) = self.__get_need_delete_files_path()
        delete_tasks = []

        for p in files:
            delete_tasks.append(lambda x=p: self.__delete(x, True))
        for p in dirs:
            delete_tasks.append(lambda x=p: self.__delete(x, False))
            
        processTask.run_tasks(delete_tasks, stop_when_failed=False)
        print(utils.color("删除完成", 32))
