Usage
=====

.. _installation:

Installation
------------

download from `github <https://github.com/Pacleme/pyPosControl>`_ page in `control position branch <https://github.com/Pacleme/pyPosControl/tree/controlPosition>`_.


Main graphical interface
------------------------

Application used to manually control turntables positions in a graphical user interface.

You can run **main.py** file. 

1. You can configure names of axis and so their number when calling the ``lauchApp`` function.
    Up to 3 axis are implemented.

.. code-block::

    launchApp(('X')) # example with one axis
    launchApp(('X','Y')) # example with two axis
    launchApp(('X','Y','T')) # example a third axis with a custom name


2. You can also configure the console printed informations with the ``logging.basicConfig`` function. 
    There is 4 levels of informations :

    * DEBUG : verbose, used when debugging the app, show all steps of actions.
    * INFO : show the global steps of actions. Recommended to look at what's currently happening.
    * WARNING : show the low incidents and important informations.
    * ERROR : show the errors, when an action fails for example.
    * CRITICAL : show only the critical errors that prevents the app from working

    You can also redirect it's informations to a file. Refer to the **logging** python documentation.

3. There is also the possibility to adjust default app window size when launched.
    Update the tuple in the ``app.geometry`` function. Unit is in px.

*from main.py file*

.. code-block::

        def launchApp(axis_names: tuple[str] = ('X','Y','Z')):
            # Current path used to find settings files
            mf.path = str(Path(__file__).parent.absolute())+"\\"

            logging.basicConfig(level=logging.INFO) # Here you can adapt showed/logged informations

            app = mf.MainApp(title="control app",axis_names=axis_names)
            app.geometry("%dx%d" % (600,app.winfo_screenheight())) # Here you can adjust default app window size

            app.mainloop()

        if __name__ == "__main__":
            print("start")

            launchApp(('X','Y')) # Here you can update axis names

            print("end")


List of positions
-----------------

Go to a list of positions and execute a function inbetween.

You can run **setofmoves.py** file.

Create a csv or xlsx file with your list of positions.

1. The first row is for axis names.
2. Second row is platines/turntables names, when at default takes the ones in ``save.json`` file.
3. Rest is absolute positions from init position when first launched. Unit is in **mm**.

*CSV example :*

.. code-block::

    x,      y
    default,default
    10,     0
    44,     22
    0,      0

Give the path to your list of positions file in the ``MoveAndMeasure.loadMoveSet`` function.

*from setofmoves.py*

.. code-block::
    
    filepath = "/master/myListOfPositionsFile.csv"

    try:
        MaM = mm.MoveAndMeasure(axis_names=('X','Y'))

        MaM.loadMoveSet(filepath=filepath) # Here you can add your list of positions file path

        MaM.run(measure,(5,5),"param1",par2="param2") # Here you can add your function inbetween positions and it's parameters

    finally:
        MaM.quit()

The function meant to be executed between each position must take a ``position`` parameter, which you can use as a tuple of int or float.
