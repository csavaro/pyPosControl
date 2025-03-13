from pathlib import Path
# import python_files.u_mainFrame as mf
import python_files.movemeasure as mm
from python_files.measures import simulateMeasure

if __name__ == "__main__":
    print("start")

    # # Current path used to find settings files
    # mf.path = str(Path(__file__).parent.absolute())+"\\"

    # app = mf.MainApp(title="test main",axis_names=('X','Y','Z'))
    # app.geometry("%dx%d" % (600,app.winfo_screenheight()))

    # app.mainloop()

    mm.path = str(Path(__file__).parent.absolute())+"\\"
    filepath = str(Path(__file__).parent.absolute())+"\\moveset.csv"

    try:

        MaM = mm.MoveAndMeasure(axis_names=('X','Y','Z'), filepath=filepath)
        MaM.loadMoveSet(filepath=filepath)

        MaM.run(simulateMeasure,(100,100,100))

    finally:
        MaM.quit()

    print("end")