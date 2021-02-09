UTILISATION:
============

Le script allProcess.sh permet de lancer toutes les parties. Il attend 4 entiers booléens:

	- Le premier commande la création des modèles strong et fast

	- Le second commande la génération des données grâce à gnugo

	- Le troisième commande l'entrainement des modèles grâce aux données précédemment générées

	- Le quatrième commande l'apprentissage par renforcement, en générant les données tirées de partie en self-play 
	et en entrainant le strong policy model grâce à elles.


EXEMPLES DE LIGNES DE COMMANDES:
================================

$ ./allProcess 1 1 1 1
 --> démarrer tous les processus créés (génération de réseaux de neurones, génération de jeux, RL training)


PROBLEMES :
===========

Nous n'avons pas pu compléter la tâche dans son intégralité. Plusieurs problèmes sont à noter:

	- Le strong policy model ne s'entraine pas, il faudrait peut-être rajouter des couches dans les données d'entrée

	- Les parties continuent trop longtemps, car le modèle ne permet pas de prédire l'action PASS
