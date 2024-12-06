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

J'ai pris la décision d'arrêter la boucle de récursivité quand on tombait sur un élément présent dans un cycle. Le dictionnaire retourné contient alors le début de la parentalité, puis une mention indiquant qu'on entre dans une boucle :
```
=== Exemple de l'entité 'PETECHIA' ===
{
"HEMORRHAGE": "In a cyclic parenthood (direct parents: http://entity/CST/HEM)",
"Hemic and Lymphatic System": 3,
"Coagulation Disorders": 2,
"Coagulation Disorders, General and NEC": 1,
"PETECHIA": 0
}
```

Cette solution permet certes d'éviter des boucles infinies, mais empêche d'obtenir l'ensemble des relations de parentés lorsque l'entité 'HEMORRHAGE' est présent dans la branche. Dans le cadre restreint de ce travail, il aurait sûrement été plus judicieux de simplement supprimer cette relation, mais je souhaitais écrire un programme flexible aux modifications du CSV. 

Ensuite, pour obtenir un résultat conforme aux exigences, j'ai d'abord initialisé un dictionnaire vide ayant pour clés l'ensemble des labels distincts, puis j'ai intégré à ce dictionnaire le résultat de la fonction *get_ontology*. Enfin, j'ai ordonné le dictionnaire dans l'ordre décroissant des valeurs. 


## Phase 3 : La conversion du programme en API, puis son déploiement avec Docker
Dans cette phase, nous expli


