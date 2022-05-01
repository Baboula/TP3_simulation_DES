# TP3_simulation_DES
Simulation à évènements discrets d'un ascenseur en fontionnement au pavillon de l'humanité de l'UQAC

Manuel d’utilisation du programme

Pour utiliser notre programme, il faut l’ouvrir avec l’IDE de votre choix. 
Ensuite, vérifier que vous disposez de la version 3 de python installée sur votre machine. 
Par la suite vous pourrez installer l'environnement de simulation simpy avec la dépendance numpy, en utilisant les commandes suivantes:

pip install simpy

pip install numpy


Une fois cette installation effectuée, il faut ouvrir le terminal python et entrer la commande:
python simulation_ascenseurs.py  pour lancer la simulation avec les paramètres par défaut.
Pour démarrer la simulation avec des paramètres spécifiques, vous pouvez utiliser la commande: 
python simulation_ascenseurs.py -h pour avoir la description de tous les paramètres pouvant être utilisés.


Et par la suite, saisir une commande au format: python simulation_ascenseurs.py -a [NombreAscenseur] -c [capacité] -v [vitesse] -o [ordonnancement] -i [true/false] -l 0.5 -d [durée en seconde]
Ainsi, l’utilisateur peut modifier la valeur des paramètres par défaut, et choisir:
Le nombre d’ascenseurs avec -a, default=1
La capacité pour chaque ascenseur avec -c , default=1
La vitesse de l’ascenseur pour passer d’un étage à l’autre avec -v, default=10 (valeur par défaut dans le sujet)
L'algorithme d’ordonnancement avec -o, default=FCFS l’autre valeur utilisable est SSTF
D’activer ou non le mode idle de l’ascenseur avec -i , default=False si vous souhaitez activer ce mode utilisez -i True cependant, si vous souhaitez le désactiver supprimez simplement l’argument -i lors de l’exécution de la commande.
De préciser la valeur de lambda dans le processus d’arrivée de Poisson avec -l ou --lamb, default=0.5 (valeur par défaut dans le sujet) 
De spécifier la durée de la simulation avec -d , default=10000
 



