# From LabView to Python

[Documentation is available here](https://pacleme.github.io/pyposcontrol/) *(still writing...)*

# Branches
### test_structure
Première prise en main de tkinter, création de la première version de l'app. Tentative d'implémentation de l'architecture MVC/MVP (Model View Controller/Model View Presenter).
### preshot
Deuxième version de l'app partiellement fonctionnelle.  
Développement après définition du cahier des charges, en attente de validation des maquettes.
### stratum
Troisième version de l'app en cours de developpement.  
Développement après première validation du cahier des charges et maquettes.  
Reprise d'une bonne partie de la branche preshot. Architecture en couches comme suit :
- Éléments graphiques : `mytools.py`, `mainFrame.py`
- Fenêtre globale, controller : `mainFrame.py` *liaison action sur éléments graphiques -> actions dans les modèles*
- Modèles, valeurs concrètes : `models.py`
- Langage de communication, commandes : `communications.py` *retourne commandes aux modèles*
- Connection au controleur : *à implémenter* 
### positionControl
Reprise du contenu de la branche stratum. Objectif rendre l'application créée dans stratum plus propre.  
Actuellement modification de l'arborescence, et mise a jour du readme.  
A venir : nettoyage des print de debug.


# settings_files
## save.json
Fichier de sauvegarde principal.
### files
Emplacement des fichier pour les configurations, controleurs et platines, simplement nommés `configurations.json`, `controleurs.json` et `platines.json` ici.  
Ces trois fichiers doivent se trouver dans un même répertoire, cependant il n'est pas obligatoire qu'ils se situent dans le répertoire `settings_files`. Il faut préciser le chemin du répertoire dans lesquels ils se trouveront dans l'attribut `path`. Cela peut être un chemin absolu, mais aussi courant, si vous utilisez *"current"* ce dernier mot sera remplacé par le chemin courant / parent au fichier main.py.
### settings
Derniers paramètres enregistrés.
### default
Valeur par défaut n'étant pas modifiables depuis l'application. Ici la vitesse, elle est en mm/s.

# python_files
## uiconsole.py
### Classes
- UiConsole: app en console, subtitue a MainFrame. Contient des methodes affichant des menus

## app/mainFrame.py
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
- ThreadExecutor : liste d'attente de threads (de taille 0).
### Usefull Functions/Methods
- FunctionPackage : prend deux listes de fonctions en parametres, execute chaque fonction de la premiere et en cas de reception d'erreur MissingValue, execute les fonctions de la deuxieme liste.

## app/guielements.py *(used to be mytools.py)*
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

# List of positions
## What you need to have
- A csv file with positions, first line should be for configuration. Position values unit is in mm from start position.
ex: 
```csv
X,Y,Z
default,Platine 1, Platine 1
0,0,0
5,0,0
5,5,0
5,5,5
0,0,0
```
- A function that takes a position as first parameter.
It can be a measurement for example.
other ex:
```python
def my_measure(position,param1,param2):
    pass
```

# Libraries
## Mandatory
- serial : **INSTALL REQUIREMENT : pyserial**
- threading
- pandas
- json
- time
- sys
- glob
- abc
## Used but optional
- pathlib
- measpy **INSTALL REQUIREMENT : measpy**
