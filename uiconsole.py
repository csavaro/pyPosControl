from pathlib import Path
import logging
import python_files.otheruses.uiconsole as uic

def launchUiConsole(axis_names = ('X','Y')):
    try:
        uic.path = str(Path(__file__).parent.absolute())+"\\"

        logging.basicConfig(level=logging.INFO)

        uicon = uic.UiConsole(axis_names)
        uicon.printCurrentPosition()
        uicon.mainMenu()

    finally:
        uicon.mControl.quit()

if __name__ == "__main__":
    print("starting")

    launchUiConsole(('X','Y'))

    print("ended")