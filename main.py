from pathlib import Path
import python_files.mainFrame as mf

if __name__ == "__main__":
    print("start")

    # Current path used to find settings files
    mf.path = str(Path(__file__).parent.absolute())+"\\"

    app = mf.MainApp(title="test main",axis_names=('X','Y','Z'))
    app.geometry("%dx%d" % (600,app.winfo_screenheight()))

    app.mainloop()