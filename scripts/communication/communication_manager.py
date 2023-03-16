import importlib
import importlib.util
import inspect
import os
import os.path

from communicator import Communicator


def __build_implementation_path__():
    """
    function for constructing the path to the directory containing the communicator implementations
    :return:
    """
    return os.path.join(str(os.getcwd()), 'impl')


class CommunicatorManager:
    """
    Manager for importing, and using available communicator-implementations
    """
    def __init__(self):
        self.implementations = self.__load_communicator_implementations__()

    def get_implementations(self) -> dict[str, Communicator]:
        """
        Fetch all available communicator implementations as a dict[name,implementation instance]

        :return: all available communicator implementations as dict[name,implementation instance]
        """
        impls = {}

        for impl in self.implementations:
            impl_instance = impl.__call__()
            impl_name = impl_instance.get_name()
            impls.__setitem__(impl_name, impl_instance)

        return impls

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

        impl_module = importlib.import_module("impl." + file_name.split('.')[0])
        impl_module_classes = inspect.getmembers(impl_module, inspect.isclass)
        impl_class = None
        for name, object in impl_module_classes:
            if not name.__contains__('Impl'):
                continue
            impl_class = object

        return impl_class
