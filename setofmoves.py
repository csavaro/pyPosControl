from pathlib import Path
import python_files.otheruses.movemeasure as mm

def measure(position,par1, par2):
    from time import sleep
    print(f"start measurement at {position} pos with par1: {par1}, par2:{par2}")
    sleep(4)
    print(f"end of measurement at {position} pos")

if __name__ == "__main__":
    print("start")

    mm.path = str(Path(__file__).parent.absolute())+"\\"
    filepath = str(Path(__file__).parent.absolute())+"\\external_files\\moveset.csv"

    try:

        MaM = mm.MoveAndMeasure(axis_names=('X','Y'))
        MaM.loadMoveSet(filepath=filepath)

        print("road map :")
        for pos in MaM.roadmap:
            print("-",pos,type(pos))

        MaM.run(measure,(5,5),"param1",par2="param2")

    finally:
        MaM.quit()

    print("end")