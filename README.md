# LMAA - Language Model Assignment Analyzer

This is LLMA (Language Model Assignment Analyser), a system
designed to collect and analyse computer science assignments with respect to modern
code generation tools. Studies about the possibilities and challenges of generator-tools
have already been published. In many of these studies small sample sizes of assignments
were solved by AI-tools. LMAA aims to be a modular, dynamic and extendable tool for
computer science educators to evaluate their curricula and courses in the light of content
generation tools. 

## How to use

### Setup

For initial setup run `setup.py`. This will create the required file structures and the database, including language
model detection.

````shell
python setup.py
````

### Run

The application can be started by running `run.py`. Make sure to finish the setup before starting the application.

````shell
python run.py
````

## Advanced management tasks

### Logging System

The logging system is structured as follows:
- **Console logging:** Only for Django logging
- **Django logging:** For Django logging and other system processes

The logfile is located according to `config/system_config.yaml`. The default location is `logs/lmaa-log.log`

### Database System

The database system is handled by [Django Models](https://docs.djangoproject.com/en/4.1/topics/db/models/). The database
structure is accordingly defined in `<appname>/models.py`.

By default `SQLite` is used as a database system. The database file is located according to `config/system_config.yaml`.
The default location is `data/lmaa-local.db`

### Communicator System

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

#### Removing outdated communicators
Outdated communicators may not necassarily be removed, but it is possible. Solutions stored in the database only contain
the name of the implementation.

When removing a communicator be sure to comply with the following instructions:

1. Delete/Remove the implementation file in `/scripts/communication/in`. If not removed, django will automatically
re-detect the Communicator upon the next startup.
2. Clean-up the database tables `llm` and `llm_property`

