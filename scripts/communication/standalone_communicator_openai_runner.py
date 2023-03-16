from scripts.communication.impl.communicator_openai_completion import OpenAICommunicatorImpl

# instantiate communicator
com = OpenAICommunicatorImpl()

# define request parameters
request_prompt = "Implement a java method 'void sum(int[] numbers)' that calculates the sum of all elements in the " \
                 "array."
request_model = "code-davinci-002"
request_parameters = {"prompt": request_prompt, 'model': request_model, 'max_tokens': 256}

# validate request parameters
valid = com.validate_request_parameters(request_parameters)
print('Request parameters are ' + ('valid' if valid else 'invalid'))

# send request
solution = com.send_request(request_parameters)
print("----------------------------------------\nGenerated Solution\n----------------------------------------")
print(solution)


