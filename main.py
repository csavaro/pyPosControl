from pathlib import Path
# import python_files.u_mainFrame as mf
import python_files.movemeasure as mm
from python_files.measures import simulateMeasure

def measure(position,par1, par2):
    from time import sleep
    print(f"start measurement at {position} pos with par1: {par1}, par2:{par2}")
    sleep(4)
    print(f"end of measurement at {position} pos")

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

        MaM = mm.MoveAndMeasure(axis_names=('X','Y'))
        MaM.loadMoveSet(filepath=filepath)

        MaM.run(measure,(5,5),"param1",par2="param2")

    finally:
        MaM.quit()

    print("end")