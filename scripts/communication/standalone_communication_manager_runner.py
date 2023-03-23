from scripts.communication import CommunicatorManager, Communicator

# load communication manager
man = CommunicatorManager()

# setup request parameters
request_prompt = "Implement a java method 'void sum(int[] numbers)' that calculates the sum of all elements in the " \
                 "array."
request_model = "code-davinci-002"
request_parameters = {"prompt": request_prompt, 'model': request_model, 'max_tokens': 256}

# select and load implementation
impl_name = 'OpenAI'
impl = man.get_implementations()[impl_name]

# print result
print("---------------------------------")
print("Communicator: " + impl_name)
print("---------------------------------")

response = impl.select_communication_content(request_parameters)
print(response.payload)

