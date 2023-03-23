# LMAA - Language Model Assignment Analyzer

## Logging System

TBD

## Database System

TBD

## Communicator System

The communicator system can be dynamically extended. Correctly configured and implemented communicators will
automatically be available in the `CommunicationManager` and the `django` frontend upon the next startup. 

#### Adding new communicators
New communicators may be added at any point to `scripts.communication.impl`. 
When implementing a new communicator be sure to comply with the following instructions:

1. Create new python file in `/scripts/communication/impl`
2. Create a class with the mandatory name-schema `___CommunicatorImpl` inheriting from `Communicator`
3. Define all request properties necessary for API calls in the class-property `properties`
   1. The property containing the user-input must always be named `prompt`
   2. Properties may have one of 3 types (str,int,float), as implemented by `PropertyType`. If additional types are
required, the frontend must be adapted
   3. A property can be mandatory or optional. Optional properties must contain a default value
   4. A property may or may not be a configuration-property. Configuration properties are properties displayed in the 
frontend form `/communication/new/configure`
4. Define the display name of the Communicator in the class-property `name`
5. Implement `__init__` containing a super-call (`super().__init__('<CommunicationName>')`)
6. Implement all abstract methods from `Communicator` as described in the documentation

The provided implementation found in `communicator_openai_chat_completion.py` may be used as a guide.

If all steps have been completed correctly the `CommunicationManager` will automatically detect the implementation and 
make it available via `get_implementations()`.

### Removing outdated communicators
Outdated communicators may not necassarily be removed, but it is possible. Solutions stored in the database only contain
the name of the implementation.

When removing a communicator be sure to comply with the following instructions:

1. Delete/Remove the implementation file in `/scripts/communication/in`. If not removed, django will automatically
re-detect the Communicator upon the next startup.
2. Clean-up the database tables `llm` and `llm_property`

