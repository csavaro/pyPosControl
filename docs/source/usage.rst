Usage
=====

.. _installation:

Installation
------------

download from `github <https://github.com/Pacleme/pyPosControl>`_ page in `control position branch <https://github.com/Pacleme/pyPosControl/tree/controlPosition>`_.


Main graphical interface
------------------------

Application used to manually control turntables positions in a graphical user interface.

*from main.py file*

.. code-block::

        def launchApp(axis_names: tuple[str] = ('X','Y','Z')):
            # Current path used to find settings files
            mf.path = str(Path(__file__).parent.absolute())+"\\"

            logging.basicConfig(level=logging.DEBUG)

            app = mf.MainApp(title="control app",axis_names=axis_names)
            app.geometry("%dx%d" % (600,app.winfo_screenheight()))

            app.mainloop()

        if __name__ == "__main__":
            print("start")

            # launchApp(('X','Y'))
            launchApp(('X','Y'))

            print("end")

End