============
RestAPY
============

***************
Introduction
***************
    RestAPY is a module made to easily create Rest APIs in Python.

    It therefore can be used to make JSON data from your projects easily accessible through a webbrowser or through API requests.

    **Note**: This documentation contains all the useful information about version 1.0.0

***************
Dependencies
***************
    All of the modules restAPY is based on are part of the default python install and therefore do not need to be installed seperately. The following list contains all of those modules:

    - socket
    - threading
    - json

***************
Code example
***************
    The following example will first create an API instance that will be accessible through the URL "http://localhost:8000/".

    Then it will tell the API what data to return when the user requests this domain at the root path ("/")

    After which the API starts listening for incoming connections.

        import restAPY
        
        api = restAPY.API(8000, "localhost")

        api.setPath("/", {"celsius":5, "fahrenheit":41})
        
        api.run()
