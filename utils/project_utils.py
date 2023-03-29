import os.path
from pathlib import Path


def find_root_path(filepath):
    """
    backtrack folder-structure starting at the given filepath and ending at LMAA root directory
    """
    path = Path(filepath)
    while not __is_root_dir__(path):
        path = path.parent.absolute()
    return path.absolute()


def __is_root_dir__(path: Path) -> bool:
    req_dirs = ['assets', 'config', 'gui', 'lmaa', 'scripts', 'templates', 'utils']
    for i in range(len(req_dirs)):
        req_dirs[i] = os.path.join(path, req_dirs[i])
    return __check_dir_list(req_dirs)


def __check_dir_list(dirs: [str]) -> bool:
    for dir in dirs:
        if not os.path.exists(dir):
            return False
    return True