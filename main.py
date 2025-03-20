from pathlib import Path
import python_files.app.mainFrame as mf

def launchApp(axis_names: tuple[str] = ('X','Y','Z')):
    # Current path used to find settings files
    mf.path = str(Path(__file__).parent.absolute())+"\\"

    app = mf.MainApp(title="control app",axis_names=axis_names)
    app.geometry("%dx%d" % (600,app.winfo_screenheight()))

    app.mainloop()

if __name__ == "__main__":
    print("start")

    launchApp(('X','Y','Z'))

    print("end")