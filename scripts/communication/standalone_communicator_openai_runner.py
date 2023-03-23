import argparse

from openai.cli import bcolors

from scripts.communication.impl.communicator_openai_chat_completion import OpenAICommunicatorImpl

# parse arguments
parser = argparse.ArgumentParser(
    prog='OpenAI Chat Standalone Runner',
    description='Script to automatically call OpenAI Chat-Completion')
parser.add_argument('-m', '--model',
                    action='store',
                    choices=['gpt-3.5-turbo'],
                    help='OpenAI model to be called - default gpt-3.5-turbo',
                    required=False,
                    default='gpt-3.5-turbo')
parser.add_argument('-p', '--prompt',
                    action='store',
                    help='Prompt to be sent the the selected OpenAI model',
                    required=True)
args = parser.parse_args()

# fetch values from parser
model = args.model
prompt = args.prompt
request_parameters = {"prompt": prompt, 'model': model}

# instantiate communicator
com = OpenAICommunicatorImpl()

# validate request parameters
valid = com.validate_request_parameters(request_parameters)
if not valid:
    print(f"{bcolors.WARNING}Error: requested parameters are not valid{bcolors.ENDC}")
    exit(1)

# send request
solution = com.send_request(request_parameters)
if solution != 200:
    print(f"{bcolors.WARNING}Error: response code {solution.code} \n {solution.payload} {bcolors.ENDC}")
    exit(1)

print("----------------------------------------\nGenerated Solution\n----------------------------------------")
print(solution.payload)
