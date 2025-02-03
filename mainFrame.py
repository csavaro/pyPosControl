import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
import mytools

class ControlFrame(tk.Frame):
    def __init__(self, master: tk.Widget, options: dict, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # ! TO CLEANUP !
        # Example
        ex_options = {
            "control1": {
                "name": "Incrémental",
                "frame": mytools.AxisFrame(None,('X','Y','Z'))
            },
            "control2": {
                "name": "Absolu",
                "frame": mytools.AxisFrame(None,('X','Y'))
            },
        }

        self.options = options
        self.pnlNavbar = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.content = None

        self.btnNav = {}
        for key,oneOption in options.items():
            self.btnNav.update(
                {
                    key:
                    tk.Button(
                        self.pnlNavbar,
                        text=oneOption["name"],
                        command=lambda k=key: self.buttonPressed(k)
                    )
                }
            )
    def setContent(self, frame: tk.Frame, event):
        ## maybe remove old layout
        self.content = frame
        ## probably apply new layout

    def buttonPressed(self, button_key):
        pass

    def apply_layout(self):
        pass

    def reset_layout(self):
        pass



if __name__ == "__main__":
    print("start")

    pnlAxis = [ 10 ] *3
    print(pnlAxis)