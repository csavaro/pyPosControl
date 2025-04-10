import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path('..').resolve()))
    print("star")
    print(str(Path(__file__,'../../../python_files').resolve()))