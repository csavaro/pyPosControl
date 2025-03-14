# Look at main.py
## What you need to have
- A csv file with positions, first line should be for configuration. Position values unit is in mm from start position.
ex: 
```csv
default,Platine 1, Platine 1
0,0,0
5,0,0
5,5,0
5,5,5
0,0,0
```
- A function that take position as first parameter.
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
- csv
- json
- time
- sys
- glob
- abc
## Used but optional
- pathlib
- measpy **INSTALL REQUIREMENT : measpy**