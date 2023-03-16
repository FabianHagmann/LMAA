def find_root_path(filepath):
    """
    backtrack folder-structure starting at the given filepath and ending at LMAA root directory
    """
    while filepath[filepath.rfind('\\') + 1:] != 'LMAA':
        filepath = filepath[:filepath.rfind('\\')]
    return filepath
