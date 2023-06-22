# BolBot

Le fichier a executer est situé dans *index.py*. *GestFichier.py* lui sert a stocker les différentes fonctions faisant le lien avec des fichiers exterieurs.
**Un fichier *config.py* est néccéssaire pour le fonctionnement du bot**. Il foit y avoir le token du bot dans un variable *token* ainsi que le chemin d'acces complet au dossier du fichier CSV pour contenir les prénom et la sauvegarde des ID/MdP pronote : *file_acces*

Un fichier log est automatiquement générer et porte le numéro de la semaine. Ex: *log_23.txt*
Un fichier csv *pronote.py* est néccésaire a la sauvegarde des ID/MdP des utilisateurs
Vous pouvez récupere la semaine actuelle avec la fonction *act_sem* dans *GestConfig.py*

Le programme néccésite la librairie **Discord**,**Discord.ext**,**cryptographie** ainsi que **pronotepy** *(et les librairies liée)*
