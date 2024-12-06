Après avoir exploré le jeu de données dans un notebook, les problèmes suivants ont été identifiés :
* Certains Parents sont inscrits comme NaN (float), ce qui posera problème dans la suite du traitement,
* Certaines Class ID partagent le même Preferred Label,
* Certaines boucles sont présentes dans la parentalité (par exemple l'entité A est le parent de l'entité B, elle-même parent de l'entité A).

Une fois ces problèmes résolus, il sera possible d'écrire une fonction récursive permettant de retracer l'ontologie pour chaque branche.