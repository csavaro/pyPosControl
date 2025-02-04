# From LabView to Python

## mytools.py
### Classes
- AxisLabeledEntry : lbl+value+speed+units
- AxisFrame
- SettingsLabeledEntry : lbl+combobox+disable entry+unit
- SettingsFrame
- ControlFrame : to go from absolute to increment movement for example
- AxisButtons : two buttons, with texts + and - used for an axis.
- AxisButtonsFrame : display buttons for each axis defined, layout from 1 axis to 3 (easily upgradable).
- ControlGeneralFrame : display current axis values, buttons to stop, set as zero and go to zero

### Usefull Functions/Methods
- searchByName : search elem from dictionary by attribute "name" and return the element with all other attributes.
- checkPosInput : force an input (ex type: DoubleVar) to be positive. Return -1 if data is not a number.