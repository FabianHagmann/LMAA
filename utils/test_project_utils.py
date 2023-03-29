import os

from utils.project_utils import find_root_path


def test_find_root_path():
    # Create some temporary directories and files
    temp_dir = 'temp'
    root_dir = os.path.join(temp_dir, 'lmaa')
    os.makedirs(root_dir)
    os.makedirs(os.path.join(root_dir, 'config'))
    os.makedirs(os.path.join(root_dir, 'utils'))
    os.makedirs(os.path.join(root_dir, 'gui'))
    os.makedirs(os.path.join(root_dir, 'scripts'))
    os.makedirs(os.path.join(root_dir, 'templates'))
    os.makedirs(os.path.join(root_dir, 'assets'))
    os.makedirs(os.path.join(root_dir, 'assets', 'images'))
    os.makedirs(os.path.join(root_dir, 'assets', 'fonts'))
    open(os.path.join(root_dir, 'lmaa.txt'), 'a').close()
    open(os.path.join(root_dir, 'config', 'config.txt'), 'a').close()
    open(os.path.join(root_dir, 'utils', 'utils.txt'), 'a').close()
    open(os.path.join(root_dir, 'gui', 'gui.txt'), 'a').close()
    open(os.path.join(root_dir, 'scripts', 'scripts.txt'), 'a').close()
    open(os.path.join(root_dir, 'templates', 'templates.txt'), 'a').close()
    open(os.path.join(root_dir, 'assets', 'images', 'image.png'), 'a').close()
    open(os.path.join(root_dir, 'assets', 'fonts', 'font.ttf'), 'a').close()

    try:
        # Test finding root directory from a subdirectory
        sub_dir = os.path.join(root_dir, 'gui', 'sub_dir')
        os.makedirs(sub_dir)
        assert find_root_path(sub_dir) == os.path.abspath(root_dir)

        # Test finding root directory from a file in a subdirectory
        file_path = os.path.join(root_dir, 'gui', 'gui.txt')
        assert find_root_path(file_path) == os.path.abspath(root_dir)

        # Test finding root directory from a file in the root directory
        file_path = os.path.join(root_dir, 'lmaa.txt')
        assert find_root_path(file_path) == os.path.abspath(root_dir)

        # Test finding root directory from a file in a subdirectory that doesn't contain all required directories
        sub_dir = os.path.join(root_dir, 'gui', 'sub_dir2')
        os.makedirs(sub_dir)
        file_path = os.path.join(sub_dir, 'file.txt')
        assert find_root_path(file_path) == os.path.abspath(root_dir)

        # Test finding root directory from a file in a subdirectory that doesn't exist
        file_path = os.path.join(root_dir, 'nonexistent', 'file.txt')
        assert find_root_path(file_path) == os.path.abspath(root_dir)

    finally:
        # Clean up temporary directories and files
        os.remove(os.path.join(root_dir, 'lmaa.txt'))
        os.remove(os.path.join(root_dir, 'config', 'config.txt'))
        os.remove(os.path.join(root_dir, 'utils', 'utils.txt'))
        os.remove(os.path.join(root_dir, 'gui', 'gui.txt'))
        os.remove(os.path.join(root_dir, 'scripts', 'scripts.txt'))
        os.remove(os.path.join(root_dir, 'templates', 'templates.txt'))
        os.remove(os.path.join(root_dir, 'assets', 'images', 'image.png'))
        os.remove(os.path.join(root_dir, 'assets', 'fonts', 'font.ttf'))
        os.removedirs('temp')
