# From LabView to Python

## uiconsole.py
### Classes
- UiConsole: app en console, subtitue a MainFrame. Contient des methodes affichant des menus

## mainFrame.py
### Classes
- MainFrame : app graphique (tk.Tk()), regroupe tous les éléments graphiques et fait le liens avec les modèles.

## connection.py
### Exceptions
- MissingValue : meant to be called when an important parameter or value is not set.
### Classes
- SerialConnection : create a serial connection by port and execute raw commands on it. Wait for an acknowledge after sending each command atm.

## communications.py
### Abstract class
- Commads : set mandatory functions for future commands like c-series. Currently there is `move` and `stop`.
### Classes
- CSeries : retourne les commandes au format c-series

## models.py
### Classes
- ModelSettings : store settings data like port, stepscales and baudrate
- ControlSettings : store control data like axis values and axis speeds.

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
- ScrollableFrame : ajoute une scrollbar et le bind de la molette.

### Usefull Functions/Methods
- searchByName : search elem from dictionary by attribute "name" and return the element with all other attributes.
- checkPosInput : force an input (ex type: DoubleVar) to be positive. Return -1 if data is not a number.