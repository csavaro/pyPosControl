from pathlib import Path
import python_files.app.mainFrame as mf
import logging
import argparse


level = logging.INFO
parser = argparse.ArgumentParser(description="Launch interface to command robot",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 )
parser.add_argument("-v","--verbose",action = "store_true",help="add debug messages")
parser.add_argument("-a",
                    "--axis",
                    nargs="*",
                    default = "X",
                    help = "Names of the axis used",
                    metavar=("X Y")
                    )

args = parser.parse_args()

if args.verbose:
    level = logging.DEBUG

def launchApp(axis_names: tuple[str] = ('X','Y','Z')):
    # Current path used to find settings files
    mf.path = str(Path(__file__).parent.absolute())+"\\"

    logging.basicConfig(level=level)

    app = mf.MainApp(title="control app",axis_names=axis_names)
    app.geometry("%dx%d" % (600,app.winfo_screenheight()))

    app.mainloop()

if __name__ == "__main__":
    print("start")

    # launchApp(('X','Y'))
    launchApp(tuple(args.axis))

    print("end")