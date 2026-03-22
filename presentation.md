# Dossier technique

## Presentation globale
Ce projet est une simulation de gestion de fourmilière, développée en Python dans le cadre des trophées NSI 2026. Le joueur doit gérer les ressources, explorer le territoire, et faire prospérer sa colonie. Le jeu combine des éléments de stratégie, de gestion et d'exploration dans un environnement dynamique.
Nous avons eu l'idée de mêler des jeux comme Rise of Kingdoms (dans l'esprit du système d'expédition) et Satisfactory (dans le développement de la colonie) aux fourmis, dont le compertement est très intéressant à étudier, afin de coller au thème de la nature.
    

## Organisation

Notre équipe est composé de deux élèves de Terminale du Lycée Montaigne;

SCHLEICHER Nikolaï;
- Structure principale du projet
- Gestionnaire d'UI (Interface utilisateur) customisé pour une meilleure personnalisation
- State de la colonie, gestion des salles et des fourmis
- Réalisation d'assets 2D pour les salles et certains icones

DISCAZEAUX Pierre;
- State pour l'exploration avec carte générée à l'aide d'un bruit de perlin
- State de combat, mini jeu stratégique avec adversaires intéligents, objets, etc.

## Vérification de l'opérationnalité

Nous avons implémenté des tests unitaires (à l'aide de `pytest`) sur les composants critiques.
En complément à cela, nous utilisons un workflow github, qui s'assure de la validation des tests sur une variété de versions de python à chaque changement.

Nous avons rencontré différents problèmes, comme:
- Problèmes de performances sur le déplacement sur la carte, réglé par le blittage seulement des parties visibles de la map à l'écran
- Problèmes au moment de changer de tour (et tout ce qui va avec)
- Trouver le plus court chemin au sein de la fourmilière dans les passages possibles, réglé par     l'utilisation d'un algorithme de recherche A*
   
## Ouverture
Nous avons de nombreuses idées d'améliorations possibles, comme le développement de nouvelles fonctionnalités (comme un systeme de déroulement de combat plus poussé), l'amélioration de l'interface utilisateur, l'optimisation des performances, ou encore l'ajout de nouveaux types d'unités ou de ressources.
Ce projet nous a permis de développer des compétences en algorithmes de recherche et en gestion de projet, et nous a donné l'occasion de travailler avec une répartition de tâches efficace au sein de notre équipe. Nous sommes fiers du travail accompli et sommes impatients de continuer à améliorer notre projet à l'avenir.
