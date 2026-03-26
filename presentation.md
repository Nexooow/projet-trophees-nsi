# Dossier technique

## Présentation globale
Ce projet est une simulation de gestion de fourmilière, développée en Python dans le cadre des Trophées NSI 2026. Le joueur doit gérer les ressources, explorer le territoire, et faire prospérer sa colonie. Le jeu combine des éléments de stratégie, de gestion et d'exploration dans un environnement dynamique.

Nous avons eu l'idée de mêler des jeux comme *Rise of Kingdoms* (dans l'esprit du système d'expédition) et *Satisfactory* (dans le développement de la colonie) aux fourmis, dont le comportement est très intéressant à étudier, afin de coller au thème de la nature.

## Organisation

Notre équipe est composée de deux élèves de Terminale du Lycée Montaigne :

**SCHLEICHER Nikolaï**
- Structure principale du projet
- Gestionnaire d'UI (Interface utilisateur) customisé pour une meilleure personnalisation
- State de la colonie, gestion des salles et des fourmis
- Réalisation d'assets 2D pour les salles et certaines icônes

**DISCAZEAUX Pierre**
- State pour l'exploration avec carte générée à l'aide d'un bruit de Perlin
- State de combat, mini-jeu stratégique avec adversaires intelligents, objets, etc.

### Utilisation de l'IA

L'intelligence artificielle a été utilisée exclusivement pour du conseil, et non la génération de code.
En effet, nous avons utilisé l'IA pour nous conseiller et nous guider dans la rédaction de tests unitaires, mais aussi pour nous guider sur certaines questions techniques, comme l'optimisation de la grille de la colonie.

## Vérification de l'opérationnalité

Nous avons implémenté des tests unitaires (à l'aide de `pytest`) sur les composants critiques.
En complément à cela, nous utilisons un workflow GitHub, qui s'assure de la validation des tests sur une variété de versions de Python à chaque changement.

Nous avons rencontré différents problèmes, comme :
- Problèmes de performances sur le déplacement sur la carte, réglé par l'affichage seulement des parties visibles de la carte à l'écran (culling).
- Problèmes au moment de changer de tour.
- Trouver le plus court chemin au sein de la fourmilière dans les passages possibles, réglé par l'utilisation d'un algorithme de recherche A*.

## Ouverture

Nous avons de nombreuses idées d'améliorations possibles :
- Nouvelles fonctionnalités pour le système de combat
- Amélioration de l'interface utilisateur
- Ajout de nouvelles unités, ressources...
- Meilleur équilibrage pour la gestion de la colonie

Ce projet nous a permis de développer des compétences en algorithmes de recherche et en gestion de projet, et nous a donné l'occasion de travailler avec une répartition de tâches efficace au sein de notre équipe. Nous sommes fiers du travail accompli et sommes impatients de continuer à améliorer notre projet à l'avenir.