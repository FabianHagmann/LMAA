import logging

import openai as openai
import yaml
from openai import OpenAIError

import config
from scripts.communication import Communicator, CommunicationResponse
from utils import project_utils


class OpenAICommunicatorImpl(Communicator):
    """
    Implementation of 'Communicator' from communication with OpenAI models
    """

    # parameter configuration
    mandatory_parameters = ['prompt', 'model']
    optional_parameters = ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']
    optional_parameter_defaults = {'temperature': 0.7,
                                   'max_tokens': 256,
                                   'top_p': 1,
                                   'frequency_penalty': 0,
                                   'presence_penalty': 0
                                   }

    def __init__(self):
        super().__init__('OpenAI')
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

    def validate_request_parameters(self, request_parameters: dict[str, str]) -> bool:
        # check if no unknown parameters are given
        for parameter in request_parameters.keys():
            if parameter not in self.mandatory_parameters and \
                    parameter not in self.optional_parameters:
                logging.error("Parameter validation failed: Unexpected parameter \'" + parameter + "\' found")
                return False

        # check if all mandatory parameters are given
        for parameter in self.mandatory_parameters:
            if parameter not in request_parameters.keys():
                logging.error("Parameter validation failed: Mandatory parameter \'" + parameter + "\' not found")
                return False
        return True

    def get_mandatory_parameters(self) -> list[str]:
        return self.mandatory_parameters

    def get_optional_parameters(self) -> list[str]:
        return self.optional_parameters

    def __send_validated_request__(self, validated_request_parameters: dict[str, str]) -> str:
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
                else self.optional_parameter_defaults['temperature'],
            max_tokens=validated_request_parameters['max_tokens'] \
                if validated_request_parameters.__contains__('max_tokens') \
                else self.optional_parameter_defaults['max_tokens'],
            top_p=validated_request_parameters['top_p'] \
                if validated_request_parameters.__contains__('top_p') \
                else self.optional_parameter_defaults['top_p'],
            frequency_penalty=validated_request_parameters['frequency_penalty'] \
                if validated_request_parameters.__contains__('frequency_penalty') \
                else self.optional_parameter_defaults['frequency_penalty'],
            presence_penalty=validated_request_parameters['presence_penalty'] \
                if validated_request_parameters.__contains__('presence_penalty') \
                else self.optional_parameter_defaults['presence_penalty'],
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
