import importlib
import importlib.util
import inspect
import os
import os.path

from utils import project_utils
from scripts.communication.communicator import Communicator


def __build_implementation_path__():
    """
    function for constructing the path to the directory containing the communicator implementations
    :return:
    """
    return os.path.join(project_utils.find_root_path(__file__), 'scripts', 'communication', 'impl')


class CommunicatorManager:
    """
    Manager for importing, and using available communicator-implementations
    """
    def __init__(self):
        self.implementations = self.__load_communicator_implementations__()

    def get_implementations(self) -> list[Communicator]:
        """
        Fetch all available communicator implementations as a list[Communicator]

        :return: all available communicator implementations as list[Communicator]
        """
        return self.implementations

    def __load_communicator_implementations__(self) -> list[Communicator]:
        """
        loads all correctly configured and implemented implementations dynamically

        :return: list of class references for implementations
        """
        impl_list = []
        impl_dir_path = __build_implementation_path__()

        for file_name in os.listdir(impl_dir_path):
            impl_class = self.__load_single_communicator_implementation__(file_name)
            if impl_class is not None:
                impl_list.append(impl_class)

        return impl_list

    def __load_single_communicator_implementation__(self, file_name) -> Communicator | None:
        """
        loads a specified implementation dynamically based on the name

        :param file_name: filename of the implementation
        :return: loaded implementation as class reference
        """
        if file_name.split('.')[0].startswith('__'):
            return None

        impl_module = importlib.import_module("scripts.communication.impl." + file_name.split('.')[0])
        impl_module_classes = inspect.getmembers(impl_module, inspect.isclass)
        impl_class = None
        for name, object in impl_module_classes:
            if not name.__contains__('Impl'):
                continue
            impl_class = object.__new__(object)

        return impl_class
