# From LabView to Python

## Branches
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