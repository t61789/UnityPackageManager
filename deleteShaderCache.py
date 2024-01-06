import utils
import shutil
import os

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
        utils.print_inline("正在删除：" + os.path.relpath(path, self.runtime.get_cur_project_path()))
        try:
            if is_file:
                os.remove(path)
            else:
                shutil.rmtree(path)
        except Exception as e:
            print(utils.color(" 失败：", 31), e.args)
            return False

        print(utils.color(" 成功", 32))
        return True
    
    def delete_shader_cache(self):
        print()

        (files, dirs) = DeleteShaderCache.__get_need_delete_files_path()

        for p in files:
            self.__delete(p, True)
        for p in dirs:
            self.__delete(p, False)

        print(utils.color("删除完成", 32))
