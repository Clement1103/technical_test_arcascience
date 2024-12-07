# Projet : Construction d'une ontologie à partir d'un fichier CSV

Le but de ce projet est de construire une représentation logique de l'Onto-X qui préserve les relations d'ancêtres (directes et indirectes) et permet ainsi de reconstruire la hiérarchie des entités.

* [L'exploration des données et leur pré-traitement](#phase-1-lexploration-des-données-et-leur-pré-traitement)
* [L'écriture de la fonction qui déduit les relations de parentés](#phase-2-lecriture-de-la-fonction-qui-déduit-les-relations-de-parentés)
* [La conversion du programme en API, puis son déploiement avec Docker](#phase-3-la-conversion-du-programme-en-api-puis-son-déploiement-avec-docker)

---

## Phase 1 : L'exploration des données et leur pré-traitement
Pour commencer, j'ai choisi de traiter les données en convertissant le CSV en DataFrame Pandas car c'est un format avec lequel je suis familier, et que j'ai déjà utilisé à de nombreuses reprises dans mes projets.

Après avoir exploré le jeu de données dans un notebook, les problèmes suivants ont été identifiés :
* Certains parents sont inscrits comme NaN (float), tandis que les autres sont des chaînes de caractères, ce qui posera problème dans la suite du traitement,
* Certaines Class ID partagent le même Preferred Label,
* Certaines boucles sont présentes dans la parentalité (par exemple l'entité A est le parent de l'entité B, elle-même parent de l'entité A).

### Remplacement des parents non-renseignés
Tout d'abord, j'ai décidé de remplacer les NaN values par la chaîne de caractère 'None', de manière à uniformiser les types dans la colonne 'Parents'. Ceci se fait simplement à l'aide de la fonction *replace_nan_values*. 

### Modification des entités partageant le même Preferred Label
Sachant qu'au final, on souhaite obtenir la représentation de parentalité d'une entité à partir de son label, il serait problématique que deux entités partagent le même label. 

J'ai d'abord pensé à supprimer les doublons, ce qui aurait créé des trous dans la parentalité, faussant les résultats finaux. J'ai donc décidé de les renommer en ajoutant simplement un indice derrière les les labels des doublons. De cette manière, on passe de cette représentation :

| Class ID        | Preferred Label | Parents         |
|-----------------|-----------------|-----------------|
| http://entity1/ | Label1          | http://entity2/ |
| http://entity2/ | Label2          | http://entity3/ |
| http://entity3/ | Label1          | http://entity4/ |

à la représentation suivante :

| Class ID        | Preferred Label | Parents         |
|-----------------|-----------------|-----------------|
| http://entity1/ | Label1          | http://entity2/ |
| http://entity2/ | Label2          | http://entity3/ |
| http://entity3/ | Label1_2        | http://entity4/ |

On conserve ainsi l'intégralité des relations. Cette méthode présente tout de même un inconvénient : pour retracer l'ontologie d'un élément qui a été renommé, il est nécessaire de saisir son nouveau label. 

Pour palier ce problème, il aurait été selon moi plus judicieux de saisir le 'Class ID' de l'entité en entrée, qui est bien unique.

### Gestion des cycles dans le DataFrame
Une des entités du DataFrame ('HEMORRHAGE') présente une boucle dans la parentalité : 

 Class ID                   | Preferred Label | Parents                               |
|----------------------------|-----------------|---------------------------------------|
| http://entity/CST/HEMHMRG  | HEMORRHAGE      | http://entity/CST/HEM                 |
| http://entity/CST/HEM          | HEMORRHAGE_2    | ... \| http://entity/CST/HEMHMRG \|...|

Ici, il aurait été plus simple de simplement supprimer cette relation de parenté, d'autant plus que 'http://entity/CST/HEM' possède plusieurs autres parents. Toutefois, j'ai pensé que dans le cas où un autre CSV serait utilisé, possédant lui aussi des boucles, il serait important de les identifier. 

En me documentant, j'ai découvert que la librairie Networkx de Python permettait d'identifier facilement les boucles dans une telle structure, ce qui m'a permis d'annoter mon DataFrame avec l'appartenance ou non de l'entité à une boucle.

Finalement, le DataFrame pré-traité aura donc la structure suivante :

 Class ID                  | Preferred Label | Parents                               | In Cycle             |
|---------------------------|-----------------|---------------------------------------|----------------------|
| http://entity/CST/HEMHMRG | HEMORRHAGE      | http://entity/CST/HEM                 | True                 
| http://entity/CST/HEM     | HEMORRHAGE_2    | ...\| http://entity/CST/HEMHMRG \|... | True                 
| http://entity/x           | LabelX          | http://entity/y                       | False                

## Phase 2 : L'écriture de la fonction qui déduit les relations de parentés
Une fois le DataFrame correctement traité, il était plus simple d'écrire la fonction permettant de déduire les relations de parenté. 

En pratique, j'ai d'abord considéré le cas simple d'une branche dans laquelle chaque entité possède un unique parent. J'ai donc écrit une fonction déterminant la profondeur de chacune des relations pour une telle branche donnée, renvoyant un dictionnaire au format suivant :
```
{
  'entité_0': 0,
  'entité_1_parent_de_0': 1,
  'entité_2_parent_de_1': 2,
  ...
}
```

Une fois cette fonction écrite, il était simple de la modifier pour qu'elle devienne récursive et s'applique lorsqu'une entité possède plusieurs parents. J'ai finalement abouti à la fonction *get_ontology*.

J'ai pris la décision d'ignorer la branche concernée par la boucle de récursivité quand on tombait sur un élément présent dans un cycle. Le dictionnaire retourné contient alors le début de la parentalité, puis une mention indiquant qu'on entre dans une boucle, et le reste de la parentalité :
```
==== Exemple avec l'entité ANEMIA ====
{
"RBC DECREASED": "Entered a cyclic parentship at level 1 (direct parents: http://entity/CST/HEM). The parenthood concerning the HEMORRHAGE_2's branch will be ignored.",
"Hemic and Lymphatic System": 3,
"Erythrocyte Abnormalities": 2,
"erythrocytes decreased": 1,
"HYPOCHLOREMIA": 0
}
```

Cette solution permet d'éviter des boucles infinies, tout en indiquant à l'utilisateur qu'une des entités fait partie d'une boucle. J'ai adopté cette solution car je la trouve versatile, et devrait rester fonctionnelle pour l'utilisation d'autres fichiers CSV.

Ensuite, pour obtenir un résultat conforme aux exigences, j'ai d'abord initialisé un dictionnaire vide ayant pour clés l'ensemble des labels distincts, puis j'ai intégré à ce dictionnaire le résultat de la fonction *get_ontology*. Enfin, j'ai ordonné le dictionnaire dans l'ordre décroissant des valeurs pour améliorer sa lisibilité. 


## Phase 3 : La conversion du programme en API, puis son déploiement avec Docker

Finalement, j'ai englobé l'ensemble du travail dans une fonction main, utilisable depuis le terminal, mais aussi dans une API avec FastAPI.
J'ai ensuite créé une image Docker, appelée 'ontology_api' contenant l'ensemble de mon travail. Elle contient tous les fichiers nécessaires à l'execution du script.

L'image est disponible sur DockerHub, et on peut la pull avec la commande suivante :
``` 
docker pull baraillecl/ontology-api:latest
```
Voici, dans chacun des cas, comment appeler l'API' :

### Avec les lignes de commande:

```commandline
docker run -e MODE=cli baraillecl/ontology-api:latest cli --label "CERVIX DISORDER" --n 10
```
Ici, on saisit plusieurs paramètres :
* --label [nom de l'entité entre guillemets] : spécifie pour quelle entité on veut obtenir l'ontologie
* --n [int] : permet de n'afficher que les n premiers éléments du dictionnaire pour améliorer la lisibilité dans le terminal. Par défaut, la valeur est fixée à 9999 pour afficher l'entièreté du dictionnaire résultant.
* --dir_csv [chemin vers le fichier CSV] : indique le chemin du CSV contenant le tableau. Par défaut, ce paramètre a la valeur 'onto_x.csv', qui est inclut dans l'image Docker.

### Avec l'API:

```commandline
docker run -e MODE=api -p 8000:8000 username/ontology-api:latest
```
