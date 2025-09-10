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

1. You need to specify the **baudrate** parameter which is for reading messages at the right frequency. Unit is **baud / second**.

2. There is also the **communication** parameter to select the language in which the commands will be sent. 
You can see the available ones in ``python_files/communications.py`` file at the ``getCommandsClass`` function.
Currently there are two languages implemented :

    - ``cseries`` : The CSeries commands used by charlyRobots for example.
    - ``test`` : A test language that is only meant for debugging.


.. _platine:

Manage available platines
-------------------------

You can add, remove or update a platine by only writting in the JSON settings files.

In the JSON file for platines *(if you don't know, you can find the path in the* ``settings_files/save.json`` *file)* platines are specified like :

.. code-block::

    {
        "Platine name": {
            "stepscale": 100,
            "vmax": 20,
            "vmin": 0.5
        },
        ...
    }

1. You need to specify the **stepscale** parameter which is used to convert the step understand by the platines to milimeters. Unit is **step/mm**.

- You can also specify **vmin** and **vmax** parameters but it is **not mandatory** unlike the previous one.
    vmin is the minimal speed and vmax the maximal speed allowed. If a speed above or below those limits are set, it will take the limits values instead.

.. _configuration:

Manage available configurations
-------------------------------

You can add, remove or update a configuration by only writting in the JSON settings files.

In the JSON file for configurations *(if you don't know, you can find the path in the* ``settings_files/save.json`` *file)* configurations are specified like :

.. code-block::

    {
        "configuration id": {
            "name": "Configuration name",
            "platineX": "Platine name",
            "platineY": "Platine name",
            "platineZ": "Platine name",
            "controller": "Controleur name",
            "port": "port name"
        },
        ...
    }

1. You need to specify **name** parameter. It will be shown in the list of configurations to select.

All of the following parameters are optional, you don't need to set all of them but once a configuration is applyied, it will unset every unset settings.

- You can specify the **platineX**, **platineY** and/or **platineZ** parameters. It should be their names written in the platine JSON file.
- You can specify the **controller** parameter. It should be the name written in the controller JSON file.
- You can specify the **port** parameter. It can be a string like ``"COM2"`` for windows OS for example.

.. _language:

Manage commands languages
-------------------------

You can intergrate a commands language using Python.
For that you need to update the ``python_files/communications.py`` file.
1. Once you're there, you need to create a new class extending the abstract class ``Commands``.
Your class can look like this for example :

.. code-block::

    class NewLanguage(Commands)
        """
        Summary:
            New language to implement
        """
        def __init__(self, axis_speeds: dict = None):
            super().__init__(axis_speeds)

        def stopCmd(self)-> list:
            return ["send stop"]

        def moveCmd(self, axis_values: dict, axis_speeds: dict = None)-> list:
            return [f"send move to {axis_values} at speeds {axis_speeds}"]

        def goHome(self, nbAxis: int)-> list:
            return [f"send go home on {nbAxis} axis"]

        def setHome(self, nbAxis: int)-> list:
            return [f"send set home on {nbAxis} axis"]

        def commandsToString(self, commands: list)-> str:
            return ["send the result"]


2. Once you created your class, you need to update the ``getCommandsClass`` function.
    You need to add an elif statement at the end that will return an instance of your class like :

.. code-block::

    def getCommandsClass(communication: str, *args, **kwargs)-> Commands:
        if str.lower(communication) == "cseries":
            return  CSeries(*args,**kwargs)
        elif str.lower(communication) == "test":
            return Test(*args,**kwargs)
        # ADD HERE
        elif str.lower(communication) == "newlanguage":
            return NewLanguage(*args,**kwargs)

3. Now it is set up, you can use your new language in the controller JSON file like that :

.. code-block::

    {
        "newController": {
            "baudrate": 9600,
            "communication": "newlanguage"
        },
        ...
    }

.. _documentation:

Update documentation
--------------------

You can update documentation by writing descriptions in the code.
Then you can generate web pages with sphinx in the ``docs/`` folder.
Use the command :

.. code-block::

    sphinx-build.exe -M html ./source ./build

Then you can take the web files and host them on your server.