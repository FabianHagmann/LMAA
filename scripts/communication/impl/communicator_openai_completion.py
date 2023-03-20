import logging

import openai as openai
import yaml
from openai import OpenAIError

import config
from scripts.communication.communicator import Communicator, CommunicationResponse
from scripts.communication.communicator import CommunicatorProperty, PropertyType
from utils import project_utils


class OpenAICommunicatorImpl(Communicator):
    """
    Implementation of 'Communicator' from communication with OpenAI models
    """

    properties = [
        CommunicatorProperty('prompt', PropertyType.str, True, ""),
        CommunicatorProperty('model', PropertyType.str, True, ""),
        CommunicatorProperty('temperature', PropertyType.float, False, 0.7),
        CommunicatorProperty('max_tokens', PropertyType.int, False, 256),
        CommunicatorProperty('top_p', PropertyType.float, False, 1),
        CommunicatorProperty('frequency_penalty', PropertyType.float, False, 0),
        CommunicatorProperty('presence_penalty', PropertyType.float, False, 0),
    ]
    name = 'OpenAI'

    def __init__(self):
        config.load_logging_config()
        OpenAICommunicatorImpl.__fetch_api_key__()

    def send_request(self, request_parameters: dict[str, str]) -> CommunicationResponse:
        # validate request parameters
        if self.validate_request_parameters(request_parameters) is False:
            logging.error("Parameter validation failed: Promoting Error")
            raise Exception("Parameter Validation failed")

        completion = None
        request_count = 0

        # send request
        try:
            completion = self.__send_validated_request__(request_parameters)
            request_count += 1
            # while solution is not finished recall api with updated prompt
            while completion['choices'][0]['finish_reason'] != 'stop':
                request_parameters['prompt'] = request_parameters['prompt'] + completion['choices'][0]['text']
                request_count += 1
                completion = self.__send_validated_request__(request_parameters)
        except OpenAIError as err:
            return self.__handle_openai_error__(err)

        # send success response
        if request_count == 1:
            # if response was completed with one api-call, send only completing
            return self.__handle_openai_success__(completion)
        else:
            # if response was completed with multiple api-calls, send entire communication history
            return self.__handle_openai_success__(completion, request_parameters['prompt'])

    def validate_request_parameters(self, request_parameters: dict[str, any]) -> bool:
        # check if no unknown parameters are given
        for parameter_key in request_parameters.keys():
            exists = False
            for prop in self.properties:
                if parameter_key == prop.name and type(request_parameters.get(parameter_key)) == prop.type.name:
                    exists = True
            if exists is False:
                logging.error("Parameter validation failed: Unexpected parameter \'" + parameter_key + "\' found")
                return False

        # check if all mandatory parameters are given
        for prop in self.properties:
            if prop.mandatory is not True:
                continue
            if request_parameters.keys().__contains__(prop.name) and type(
                    request_parameters.get(prop.name)) == prop.type:
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
        :return: openAI Completion
        """
        return openai.Completion.create(
            model=validated_request_parameters['model'],
            prompt=validated_request_parameters['prompt'],
            temperature=validated_request_parameters['temperature'] \
                if validated_request_parameters.__contains__('temperature') \
                else CommunicatorProperty.fetch_default_value(self.properties, 'temperature'),
            max_tokens=validated_request_parameters['max_tokens'] \
                if validated_request_parameters.__contains__('max_tokens') \
                else CommunicatorProperty.fetch_default_value(self.properties, 'max_tokens'),
            top_p=validated_request_parameters['top_p'] \
                if validated_request_parameters.__contains__('top_p') \
                else CommunicatorProperty.fetch_default_value(self.properties, 'top_p'),
            frequency_penalty=validated_request_parameters['frequency_penalty'] \
                if validated_request_parameters.__contains__('frequency_penalty') \
                else CommunicatorProperty.fetch_default_value(self.properties, 'frequency_penalty'),
            presence_penalty=validated_request_parameters['presence_penalty'] \
                if validated_request_parameters.__contains__('presence_penalty') \
                else CommunicatorProperty.fetch_default_value(self.properties, 'presence_penalty'),
        )

    @staticmethod
    def __fetch_api_key__() -> None:
        """
        static method for fetching the api key when initializing
        """
        logging.debug("Fetching API Key")
        config_stream = open(project_utils.find_root_path(__file__) + '/config/system_config.yaml', 'r')
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
    def __handle_openai_success__(completion, optional_prompt=None):
        """
        static method for handling a successful openAi response

        :param completion: generated completion
        :param optional_prompt: optional existing prompt
        :return: communication response containing response information
        """
        if optional_prompt is None:
            return CommunicationResponse(200, completion['choices'][0]['text'])
        else:
            return CommunicationResponse(200, optional_prompt + completion['choices'][0]['text'])
