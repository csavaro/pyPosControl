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
                        command=lambda ct=oneOption["frame"]: self.setContent
                    )
                }
            )



if __name__ == "__main__":
    print("start")