UTILISATION:
============

Le script allProcess.sh permet de lancer toutes les parties. Il attend 4 entiers booléens:

	- Le premier commande la création des modèles strong et fast

	- Le second commande la génération des données grâce à gnugo

	- Le troisième commande l'entrainement des modèles grâce aux données précédemment générées

	- Le quatrième commande l'apprentissage par renforcement, en générant les données tirées de partie en self-play 
	et en entrainant le strong policy model grâce à elles.



PROBLEMES :
===========

Nous n'avons pas pu compléter la tâche dans son intégralité. Plusieurs problèmes sont à noter:

	- Le strong policy model ne s'entraine pas, il faudrait peut-être rajouter des couches dans les données d'entrée

	- Les parties continuent trop longtemps, car le modèle ne permet pas de prédire l'action PASS



EXEMPLES DE LIGNES DE COMMANDES:
================================

python3 localGame.py
--> Va lancer un match myPlayer.py contre myPlayer.py

python3 namedGame.py myPlayer randomPlayer
--> Va lancer un match entre votre joueur (NOIRS) et le randomPlayer
 (BLANC)

 python3 namedGame gnugoPlayer myPlayer
 --> gnugo (level 0) contre votre joueur (très dur à battre)
