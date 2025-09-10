maintenance
===========

.. _controller:

Manage available controllers
----------------------------

You can add, remove or update a controller by only writting in the JSON settings files.

In the JSON file for controllers *(if you don't know, you can find the path in the* ``settings_files/save.json`` *file)* controllers are specified like :

.. code-block::
    {
        "Controller name": {
            "baudrate": 9600,
            "communication": "commands language"
        },
        ...
    }

- You need to specify the **baudrate** parameter which is for reading messages at the right frequency. Unit is in **baud / second**.

- There is also the **communication** parameter to select the language in which the commands will be sent. 
You can see the available ones in ``python_files/communications.py`` file at the ``getCommandsClass`` function.
Currently there are two languages implemented :
    - ``cseries`` : The CSeries commands used by charlyRobots for example.
    - ``test`` : A test language that is only meant for debugging.


.. _language:

Manage commands languages
-------------------------

You can intergrate a commands language using Python.
For that you need to update the ``python_files/communications.py`` file.
Once there, you need to create 