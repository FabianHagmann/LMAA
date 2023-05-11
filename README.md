# LMAA - Language Model Assignment Analyzer

This is LLMA (Language Model Assignment Analyser), an all-round software-system for uploading, solving and analysing
educational assignments. With LLMs on the rise, educators face the challenge of considering the implications of
generated content when creating exercises and exams. LMAA is a platform designed for collecting existing and novel
assignments and comparing them in terms of language model generability. The resulting information, may give educators
insight into the current state of LLMs in their field of work and support them in creating novel assignments which
are not so easily solvable by language models.

## Table of Contents

1. How to use
    1. Setup
    2. Run
2. Advanced management tasks
    1. Logging system
    2. Database system
    3. Communication system
3. More information

## 1. How to use

The LMAA-Application is split into four primary components: Assignments, Communication, Testing and Visualisation.

To start, an educator may enter assignments and classification data. For assignments many language models may be called
multiple times to generate a solution. To test solutions, educators may add and execute testcases. To get an overview,
the test results and additional factors can be visualised.

### 1.1. Setup

For initial setup run `setup.py`. This will create the required file structures and the database, including language
model detection.

````shell
python setup.py
````

### 1.2. Run

The application can be started by running `run.py`. Make sure to finish the setup before starting the application.

````shell
python run.py
````

## 2. Advanced management tasks

#### 2.1. Logging System

The logging system is structured as follows:

- **Console logging:** Only for Django logging
- **Django logging:** For Django logging and other system processes

The logfile is located according to `config/system_config.yaml`. The default location is `logs/lmaa-log.log`

#### 2.2. Database System

The database system is handled by [Django Models](https://docs.djangoproject.com/en/4.1/topics/db/models/). The database
structure is accordingly defined in `<appname>/models.py`.

By default `SQLite` is used as a database system. The database file is located according to `config/system_config.yaml`.
The default location is `data/lmaa-local.db`

#### 2.3. Communicator System

The communicator system can be dynamically extended. Correctly configured and implemented communicators will
automatically be available in the `CommunicationManager` and the `django` frontend upon the next startup.

##### 2.3.1. Adding new communicators

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

##### 2.3.2. Removing outdated communicators

Outdated communicators may not necassarily be removed, but it is possible. Solutions stored in the database only contain
the name of the implementation.

When removing a communicator be sure to comply with the following instructions:

1. Delete/Remove the implementation file in `/scripts/communication/in`. If not removed, django will automatically
   re-detect the Communicator upon the next startup.
2. Clean-up the database tables `llm` and `llm_property`

## 3. More information

LMAA was developed as a part of the thesis *Large language models in computer science education: Collecting and 
analysing LLM performance for introductory programming courses* at TU Wien Informatics by Fabian Hagmann.