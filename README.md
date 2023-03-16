# LMAA - Language Model Assignment Analyzer

## Logging System

TBD

## Database System

TBD

## Communicator System

The communicator system can be dynamically extended. Correctly configured and implemented communicators will
automatically be available in the `CommunicationManager`. 

#### Adding new communicators
When implementing a new communicator be sure to comply with the following instructions:

1. Create new python file in `/scripts/communication/impl`
2. Create a class with the mandatory name-schema `___CommunicatorImp` inheriting from `Communicator`
3. Define necessary properties `mandatory_parameters` and `optional_parameters`
4. Implement `__init__` containing a super-call (`super().__init__('<CommunicationName>')`)
5. Implement all abstract methods from `Communicator` as described in the documentation

If all steps have been completed correctly the `CommunicationManager` will automatically detect the implementation and 
make it available via `get_implementations()`. The key of the resulting `dict[str,Communicator]` is the 
`<CommunicationName>` from step 4.

