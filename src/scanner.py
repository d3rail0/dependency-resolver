import os
from typing import Tuple
from clang.cindex import TranslationUnit, FileInclusion, Index
from global_logger import Log

class DependencyScanner:

    SUPPORTED_FILES = [".cpp", ".c", ".hpp", ".h"]

    glob_log: Log = Log.get_logger(name="DepdendencyScanner", logs_dir=os.path.abspath("./log"))

    def __init__(self) -> None:
        self.cindex = Index.create()

    def __norm_path(self, path:str) -> str:
        return path.replace("\\", "/")
    
    def is_valid_project_file(self, filename:str) -> int:
        """ Returns index that represents a file extension
        from SUPPORTED_FILES.
        """
        for i, ext in enumerate(self.SUPPORTED_FILES):
            if filename.endswith(ext):
                return i

        return -1

    def get_project_files(self, start_dir:str) -> list[Tuple[str, int]]:
        project_files = []

        for root, dirs, files in os.walk(start_dir):
            for path in files:
                file_type = self.is_valid_project_file(path)
                if file_type!=-1:                    
                    project_files.append((os.path.join(root,path), file_type))

        return project_files

    def get_includes(self, path:str) -> list[str]:

        self.glob_log.info(f"Parsing {path}")

        translation_unit = self.cindex.parse(
            path, 
            options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
        )

        return [
            self.__norm_path(str(incl.include)) for incl in translation_unit.get_includes()
            if incl.depth == 1
        ]

    def scan_dir(self, path_dir:str) -> dict[str, list[str]]:
        """ Scans all supported files starting from path_dir
        including subdirectories.
        Returns: Dictionary with key being project file and value is
        a list of its dependencies.
        """

        path_dir = self.__norm_path(path_dir) 

        self.glob_log.info(f"Scan started {path_dir}")

        dep_map = {}
        project_files = self.get_project_files(path_dir)

        for (file, file_type) in project_files:
            includes = self.get_includes(file)
            dep_map[file] = includes
        
        self.glob_log.info(f"Scan complete!")

        return dep_map
    