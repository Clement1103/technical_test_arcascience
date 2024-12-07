*ENGLISH VERSION BELOW*

# Projet : Construction d'une ontologie à partir d'un fichier CSV

Le but de ce projet est de construire une représentation logique de l'Onto-X qui préserve les relations d'ancêtres (directes et indirectes) et permet ainsi de reconstruire la hiérarchie des entités.

J'ai divisé mon approche en trois phases distinctes :
1. [Phase 1 : L'exploration des données et leur pré-traitement](#phase-1--lexploration-des-données-et-leur-pré-traitement)
2. [Phase 2 : L'écriture de la fonction qui déduit les relations de parentés](#phase-2--lécriture-de-la-fonction-qui-déduit-les-relations-de-parentés)
3. [Phase 3 : La conversion du programme en API, puis son déploiement avec Docker](#phase-3--la-conversion-du-programme-en-api-puis-son-déploiement-avec-docker)

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

J'ai d'abord pensé à supprimer les doublons, ce qui aurait créé des trous dans la parentalité, faussant les résultats finaux. J'ai donc décidé de les renommer en ajoutant simplement un indice derrière les labels des doublons. De cette manière, on passe de cette représentation :

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

Ici, il aurait été plus simple de supprimer cette relation de parenté, d'autant plus que 'http://entity/CST/HEM' possède plusieurs autres parents. Toutefois, j'ai pensé que dans le cas où un autre CSV serait utilisé, possédant lui aussi des boucles, il serait important de les identifier. 

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
"RBC DECREASED": "Entered a cyclic parenthood at level 1 (direct parents: http://entity/CST/HEM). The parenthood concerning the HEMORRHAGE_2's branch will be ignored.",
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
* --dir_csv [chemin vers le fichier CSV] : indique le chemin du CSV contenant le tableau. Par défaut, ce paramètre a la valeur 'onto_x.csv', qui est inclus dans l'image Docker.

L'ontologie s'affiche alors directement dans le terminal.

### Avec l'API:
On expose l'API au port 8000 :
```commandline
 docker run -e MODE=api -p 8000:8000 baraillecl/ontology-api:latest api
```

**Swagger UI**

J'ai d'abord testé l'API grâce à Swagger UI en utilisant la démarche suivante :
* Je me suis connecté à http://localhost:8000/docs depuis mon navigateur,
* J'ai ouvert le menu déroulant de l'ontology-api,
* J'ai cliqué sur le bouton "Try it out",
* Puis j'ai envoyé une requête en modifiant les paramètres qui étaient les suivants par défaut :
``` 
{
  "dir_csv": "onto_x.csv",
  "label": "string",
  "n": 9999
}
```
Il est possible de laisser les valeurs par défaut de dir_csv et n, qui correspondent respectivement au chemin d'accès du CSV (directement contenu dans l'image), puis au nombre d'entités affichées dans la réponse. Il est nécessaire de renseigner le label correspondant à l'entité dont on veut l'ontologie.

**Requêtes Curl**

Pour finir, j'ai vérifié que l'API était bien requêtable par des commandes curl dans le terminal.
```commandline
curl -X POST "http://localhost:8000/query-ontology/" -H "Content-Type: application/json" -d '{
  "dir_csv": "onto_x.csv",
  "label": "CERVIX DISORDER",
  "n": 10  
}'
```
Les paramètres sont les mêmes que dans la rubrique précédente. 

Aussi bien en utilisant Swagger que Curl, les réponses obtenues correspondent à l'ontologie pour l'entité sélectionnée.

---

## Temps consacré à chaque étape
* Phase 1 **(~1h45)** : J'ai lu l'énoncé du projet à la réception du dépôt (jeudi midi). J'ai commencé à coder seulement le lendemain matin (vendredi 9h30), en ayant déjà une vague idée de ce qu'il fallait faire grâce à ma lecture de la veille. J'ai du me documenté sur les graphes et sur la librairie Networkx, ce qui m'a pris du temps pour finalement terminer le pre-processing des données à 11h15.


* Phase 2 **(~1h50)** : J'ai directement implémenté une fonction qui marchait pour le cas simple de mono-parentalité, puis j'en ai rapidement déduit la fonction finale avec récursivité, que j'avais fini à 12h30. Pour gagner du temps, j'ai généré puis corrigé les descriptions de mes fonctions à l'aide de ChatGPT, ce qui m'a pris environ 15 minutes. Enfin, j'ai consacré ~20 minutes le lendemain (samedi matin) à une modification de la gestion des boucles.


* Phase 3 **(~2h)** : J'ai rapidement intégré mes fonctions dans une API requêtable soit via des lignes de commande, soit via FastAPI, mais j'ai rencontré quelques difficultés à combiner les deux lors du déploiement sous Docker. Par ailleurs, je souhaitais tester mon API sur une autre machine, sur laquelle je n'avais pas encore Docker. La phase de test a donc été plutôt longue, et j'aurais finalement consacré ~2h à cette phase.


* Ecriture README **(~1h30)** : J'ai essayé de rédiger un README exhaustif comprenant l'intégralité de ma démarche, ce qui m'a pris environ 1h30.


---

# Project: Building an ontology from a CSV file

The aim of this project is to build a logical representation of Onto-X that preserves ancestor relations (direct and indirect) and thus enables the hierarchy of entities to be reconstructed.

I divided my approach into three different phases:
1. [Phase 1: Data exploration and pre-processing](#phase-1-data-exploration-and-pre-processing)
2. [Phase 2: Writing the function that deduces parent relationships](#phase-2-writing-the-function-that-deduces-parent-relationships)
3. [Phase 3: Converting the program into an API, then deploying it with Docker](#phase-3-converting-the-program-into-an-api-then-deploying-it-with-docker)

---

## Phase 1: Data exploration and pre-processing
To begin with, I chose to process the data by converting the CSV into DataFrame Pandas, as this is a format with which I'm familiar, and which I've already used on numerous occasions in my projects.

After exploring the dataset in a notebook, the following problems were identified:
* Some parents are listed as NaN (float), while the others are strings, which will cause problems in further processing,
* Some Class IDs share the same Preferred Label,
* Some loops are present in parenthood (e.g. entity A is the parent of entity B, itself the parent of entity A).

### Replacing non-registered parents
First of all, I decided to replace the NaN values with the string 'None', to standardize the types in the 'Parents' column. This is simply done using the *replace_nan_values* function. 

### Modification of entities sharing the same Preferred Label
Knowing that, ultimately, we want to obtain an entity's parenthood representation from its label, it would be problematic for two entities to share the same label. 

I first thought of deleting the duplicates, which would have created holes in the parentality, distorting the final results. So I decided to rename them by simply adding a subscript behind the duplicate labels. In this way, we go from this representation:

| Class ID        | Preferred Label | Parents         |
|-----------------|-----------------|-----------------|
| http://entity1/ | Label1          | http://entity2/ |
| http://entity2/ | Label2          | http://entity3/ |
| http://entity3/ | Label1          | http://entity4/ |

to the following one:

| Class ID        | Preferred Label | Parents         |
|-----------------|-----------------|-----------------|
| http://entity1/ | Label1          | http://entity2/ |
| http://entity2/ | Label2          | http://entity3/ |
| http://entity3/ | Label1_2        | http://entity4/ |


In this way, all relationships are preserved. However, this method does have one drawback: to trace the ontology of an element that has been renamed, it is necessary to enter its new label. 

To overcome this problem, I think it would have been wiser to enter the 'Class ID' of the input entity, which is indeed unique.

### Cycle management in the DataFrame
One of the entities in the DataFrame ('HEMORRHAGE') has a loop in its parentage: 

 Class ID                   | Preferred Label | Parents                               |
|----------------------------|-----------------|---------------------------------------|
| http://entity/CST/HEMHMRG  | HEMORRHAGE      | http://entity/CST/HEM                 |
| http://entity/CST/HEM          | HEMORRHAGE_2    | ... \| http://entity/CST/HEMHMRG \|...|

Here, it would have been simpler to simply remove this relationship, especially as 'http://entity/CST/HEM' has several other parents. However, I thought that if another CSV was used, which also had loops, it would be important to identify them. 

While researching, I discovered that Python's Networkx library could easily identify loops in such a structure, allowing me to annotate my DataFrame with the entity's loop membership or otherwise.

In the end, the pre-processed DataFrame will have the following structure:


 Class ID                  | Preferred Label | Parents                               | In Cycle             |
|---------------------------|-----------------|---------------------------------------|----------------------|
| http://entity/CST/HEMHMRG | HEMORRHAGE      | http://entity/CST/HEM                 | True                 
| http://entity/CST/HEM     | HEMORRHAGE_2    | ...\| http://entity/CST/HEMHMRG \|... | True                 
| http://entity/x           | LabelX          | http://entity/y                       | False                

## Phase 2: Writing the function that deduces parent relationships
Once the DataFrame had been correctly processed, it was easier to write the function that deduces the parent relationships. 

In practice, I first considered the simple case of a branch in which each entity has a single parent. I then wrote a function determining the depth of each relationship for such a given branch, returning a dictionary in the following format:
```
{
  entity_0': 0,
  entity_1_parent_of_0': 1,
  entity_2_parent_of_1': 2,
  ...
}
```

Once this function had been written, it was a simple matter to modify it so that it became recursive and applied when an entity had several parents. I finally ended up with the *get_ontology* function.

I decided to ignore the branch concerned by the recursion loop when we came across an element present in a cycle. The returned dictionary then contains the start of the parentology, followed by an indication that we're entering a loop, and the rest of the parentology:
```
==== Example with the ANEMIA entity ====
{
“RBC DECREASED": ”Entered a cyclic parenthood at level 1 (direct parents: http://entity/CST/HEM). The parenthood concerning the HEMORRHAGE_2's branch will be ignored.”,
“Hemic and Lymphatic System": 3,
“Erythrocyte Abnormalities": 2,
“erythrocytes decreased": 1,
“HYPOCHLOREMIA": 0
}
```

This solution avoids infinite loops, while indicating to the user that one of the entities is part of a loop. I've adopted this solution because I find it versatile, and should remain functional when using other CSV files.

Next, to obtain a result that complies with the requirements, I first initialized an empty dictionary with all the distinct labels as keys, then I integrated the result of the *get_ontology* function into this dictionary. Finally, I ordered the dictionary in descending order of values to improve its readability. 


## Phase 3: Converting the program into an API, then deploying it with Docker

Finally, I wrapped up all the work in a main function, usable from the terminal, but also in an API with FastAPI.
I then created a Docker image, called 'ontology_api', containing all my work. It contains all the files needed to run the script.

The image is available on DockerHub, and you can pull it with the following command:
``` 
docker pull baraillecl/ontology-api:latest
```
Here's how to call the API in each case:

### With command lines:

```commandline
docker run -e MODE=cli baraillecl/ontology-api:latest cli --label “CERVIX DISORDER” --n 10
```

Here, we enter several parameters:
--label [entity name in quotation marks]: specifies the entity for which the ontology is to be obtained.
--n [int]: allows you to display only the first n elements of the dictionary, to improve readability in the terminal. By default, the value is set to 9999 to display the entire resulting dictionary.
--dir_csv [path to CSV file]: indicates the path to the CSV file containing the table. By default, this parameter has the value 'onto_x.csv', which is included in the Docker image.

The ontology is then displayed directly in the terminal.

### With the API:
The API is exposed on port 8000:
```commandline
 docker run -e MODE=api -p 8000:8000 baraillecl/ontology-api:latest api
```

**Swagger UI**

I first tested the API with Swagger UI using the following procedure:
* I connected to http://localhost:8000/docs from my browser,
* I opened the ontology-api drop-down menu,
* I clicked on the “Try it out” button,
* Then I sent a query, modifying the default parameters:
``` 
{
  “dir_csv": ‘onto_x.csv’,
  “label": ‘string’,
  “n": 9999
}
```

You can leave the default values for dir_csv and n, which correspond respectively to the CSV path (directly contained in the image), then to the number of entities displayed in the response. It is necessary to fill in the label corresponding to the entity whose ontology you want.

**Curl queries**

Finally, I checked that the API could be queried by curl commands in the terminal.
```commandline
curl -X POST “http://localhost:8000/query-ontology/” -H “Content-Type: application/json” -d '{
  “dir_csv": ‘onto_x.csv’,
  “label": ‘CERVIX DISORDER’,
  “n": 10  
}'
```
The parameters are the same as in the previous section. 

Using both Swagger and Curl, the responses obtained correspond to the ontology for the selected entity.

---

## Time spent on each stage
* Phase 1 **(~1h45)**: I read the project brief when I received the deposit (Thursday noon). I didn't start coding until the next morning (Friday 9:30am), already having a vague idea of what to do thanks to my reading the day before. I had to read up on graphs and the Networkx library, which took me a while to finish pre-processing the data at 11:15am.


* Phase 2 **(~1h50)**: I directly implemented a function that worked for the simple case of mono-parentality, then quickly deduced the final function with recursion, which I finished at 12:30. To save time, I generated and then corrected my function descriptions using ChatGPT, which took me about 15 minutes. Finally, I spent ~20 minutes the next day (Saturday morning) on a loop management modification.


* Phase 3 **(~2h)**: I quickly integrated my functions into an API that could be queried either via command lines or via FastAPI, but I encountered some difficulties combining the two when deploying under Docker. What's more, I wanted to test my API on another machine, on which I didn't yet have Docker. The testing phase was therefore rather long, and I ended up spending ~2h on it.


* README writing **(~1h30)**: I tried to write an exhaustive README including my entire approach, which took about 1h30.
