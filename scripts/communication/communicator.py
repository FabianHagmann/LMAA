from abc import ABC, abstractmethod


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


class Communicator(ABC):
    """
    Abstract class for all communicators
    """

    def __init__(self, name):
        self.name = name

    @property
    @abstractmethod
    def mandatory_parameters(self) -> list[str]:
        """
        Property containing all configured mandatory parameters.
        """
        pass

    @property
    @abstractmethod
    def optional_parameters(self) -> list[str]:
        """
        Property containing all configured optional parameters
        """
        pass

    @abstractmethod
    def send_request(self, request_parameters: dict[str, str]) -> CommunicationResponse:
        """
        Perform an api-call with the given request parameters

        :param request_parameters: parameters for api-call, validity of parameters is not required
        :return: current response-code
        """
        pass

    @abstractmethod
    def validate_request_parameters(self, request_parameters: dict[str, str]) -> bool:
        """
        Check if the given request-parameters are valid for the implementation

        :param request_parameters: request-parameters to be checked
        :return: true if all mandatory parameters and no invalid parameters are given
        """
        pass

    @abstractmethod
    def get_mandatory_parameters(self) -> list[str]:
        """
        Fetch all available mandatory parameters

        :return: list of mandatory parameters as str
        """
        pass

    @abstractmethod
    def get_optional_parameters(self) -> list[str]:
        """
        Fetch all available optional parameters

        :return: list of optional parameters as str
        """
        pass

    def get_name(self) -> str:
        """
        Fetch the configured name of the Communicator.

        :return: name as str
        """
        return self.name
