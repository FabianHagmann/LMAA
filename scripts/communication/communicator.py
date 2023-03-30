from abc import ABC, abstractmethod
from enum import IntEnum


class CommunicationResponse:
    """
    Class to represent a communication response containing response-code and text
    """

    def __init__(self, code: int, payload: str):
        self.code = code
        self.payload = payload

    def __str__(self):
        return "[" + str(self.code) + "]\n" + self.payload

    def get_code(self) -> int:
        """
        fetch the current response-code
        :return: current response-code
        """
        return self.code

    def get_payload(self) -> str:
        """
        fetch the current response payload
        :return: current response payload
        """
        return self.payload


class PropertyType(IntEnum):
    int = 1
    float = 2
    str = 3
    select = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class CommunicatorProperty:
    def __init__(self, name: str, type: PropertyType, mandatory, default, configuration):
        super().__init__()
        self.name = name
        self.type = type
        self.mandatory = mandatory
        self.default = default
        self.configuration = configuration

    @staticmethod
    def fetch_default_value(props: list, searched_name: str) -> str | int | float:
        for prop in props:
            if prop.name == searched_name:
                return prop.default
        return -1


class Communicator(ABC):
    """
    Abstract class for all communicators
    """

    @property
    @abstractmethod
    def properties(self) -> list[CommunicatorProperty]:
        """
        Property containing all configured parameters.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Fetch the configured name of the Communicator.

        :return: name as str
        """
        pass

    @abstractmethod
    def send_request(self, request_parameters: dict[str, any]) -> CommunicationResponse:
        """
        Perform an api-call with the given request parameters

        :param request_parameters: parameters for api-call, validity of parameters is not required
        :return: current response-code
        """
        pass

    @abstractmethod
    def validate_request_parameters(self, request_parameters: dict[str, any]) -> bool:
        """
        Check if the given request-parameters are valid for the implementation

        :param request_parameters: request-parameters to be checked
        :return: true if all mandatory parameters and no invalid parameters are given
        """
        pass

    @abstractmethod
    def get_mandatory_parameters(self) -> list[CommunicatorProperty]:
        """
        Fetch all available mandatory parameters

        :return: list of mandatory parameters as CommunicatorProperty
        """
        pass

    @abstractmethod
    def get_optional_parameters(self) -> list[CommunicatorProperty]:
        """
        Fetch all available optional parameters

        :return: list of optional parameters as CommunicatorProperty
        """
        pass

    @abstractmethod
    def get_property_options(self, prop_name: str) -> dict[str, str]:
        """
        Fetch available options for select properties

        If the implementation contains a property of type SELECT you may provide the frontend with available options.
        Depending on the parameter 'prop_name' you may return these options.

        :param prop_name: name of the property for which options should be returned
        :return: dict[str,str] containing a dict with display-name:value
        """
        pass
