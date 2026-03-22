# Dossier technique

## Presentation globale

intérêt pour les fourmi => gestion de fourmilières + idée d'exploration
TODO: compléter cette partie

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

