import logging
import os.path

import openai as openai
import yaml
from openai import OpenAIError

import config
from scripts.communication.communicator import Communicator, CommunicationResponse
from scripts.communication.communicator import CommunicatorProperty, PropertyType
from utils import project_utils


class OpenAICommunicatorImpl(Communicator):
    """
    Implementation of 'Communicator' from communication with OpenAI chat models
    """

    system_description = "You are a programmer writing java programs for introductory programming lectures"
    properties = [
        CommunicatorProperty('model', PropertyType.str, True, "", True),
        CommunicatorProperty('prompt', PropertyType.str, True, "", False)
    ]
    name = 'OpenAI Chat'

    def __init__(self):
        config.load_logging_config()
        OpenAICommunicatorImpl.__fetch_api_key__()

    def send_request(self, request_parameters: dict[str, str]) -> CommunicationResponse:
        # validate request parameters
        if self.validate_request_parameters(request_parameters) is False:
            logging.error("Parameter validation failed: Promoting Error")
            raise Exception("Parameter Validation failed")

        completion = None
        OpenAICommunicatorImpl.__fetch_api_key__()

        # send request
        try:
            completion = self.__send_validated_request__(request_parameters)
        except OpenAIError as err:
            return self.__handle_openai_error__(err)

        return self.__handle_openai_success__(completion)

    def validate_request_parameters(self, request_parameters: dict[str, any]) -> bool:
        # check if no unknown parameters are given
        for parameter_key in request_parameters.keys():
            exists = False
            for prop in self.properties:
                if parameter_key == prop.name and type(
                        request_parameters.get(parameter_key)).__name__ == prop.type.name:
                    exists = True
            if exists is False:
                logging.error("Parameter validation failed: Unexpected parameter \'" + parameter_key + "\' found")
                return False

        # check if all mandatory parameters are given
        for prop in self.properties:
            if prop.mandatory is not True:
                continue
            if request_parameters.keys().__contains__(prop.name) and type(
                    request_parameters.get(prop.name)).__name__ == prop.type.name:
                continue
            else:
                return False
        return True

    def get_mandatory_parameters(self) -> list[CommunicatorProperty]:
        mandatory_properties = []

        for prop in self.properties:
            if prop.mandatory:
                mandatory_properties.append(prop)

        return mandatory_properties

    def get_optional_parameters(self) -> list[CommunicatorProperty]:
        optional_properties = []

        for prop in self.properties:
            if not prop.mandatory:
                optional_properties.append(prop)

        return optional_properties

    def __send_validated_request__(self, validated_request_parameters: dict[str, any]) -> str:
        """
        submethod for sending a request containing validated request data

        :param validated_request_parameters: validated request data
        :return: openAI ChatCompletion
        """

        messages = self.__build_message_from_prompt_and_system_description(validated_request_parameters['prompt'],
                                                                           self.system_description)

        return openai.ChatCompletion.create(
            model=validated_request_parameters['model'],
            messages=messages
        )

    @staticmethod
    def __fetch_api_key__() -> None:
        """
        static method for fetching the api key when initializing
        """
        logging.debug("Fetching API Key")
        config_stream = open(os.path.join(project_utils.find_root_path(__file__), 'config', 'system_config.yaml'), 'r')
        config_map = yaml.safe_load(config_stream)
        openai.api_key = config_map['communicator']['openai-completion']['apikey']

    @staticmethod
    def __handle_openai_error__(error):
        """
        static method for handling an openAi error response

        :param error: error from 'OpenAiError'
        :return: communication response containing error information
        """
        return CommunicationResponse(error.http_status, error.user_message)

    @staticmethod
    def __handle_openai_success__(completion):
        """
        static method for handling a successful openAi response

        :param completion: generated completion
        :param optional_prompt: optional existing prompt
        :return: communication response containing response information
        """

        result = ''
        for choice in completion.choices:
            result += choice.message.content

        return CommunicationResponse(200, result)

    @staticmethod
    def __build_message_from_prompt_and_system_description(prompt: str, system_desc: str) -> str:
        system_message = {'role': 'system', 'content': system_desc}
        user_message = {'role': 'user', 'content': prompt}
        messages = [system_message, user_message]

        return messages
