# Rise of the Anthill

**Rise of the Anthill** est un jeu de gestion et de simulation dans lequel vous guidez une colonie de fourmis depuis ses premiers instants jusqu'à en faire une fourmilière prospère. Creusez des galeries, assignez des rôles à vos fourmis, gérez vos ressources et envoyez des expéditions explorer le monde extérieur.

---

## Sommaire

├─ [Fonctionnalités](#fonctionnalites)  
├─ [Installation & Démarrage](#installation)  
├─ [Structure du projet](#structure)  
├─ [Auteurs](#auteurs)  
└─ [Documentation](/docs/introduction.md)

---

<a id="fonctionnalites"></a>
## Fonctionnalités

- **Gestion de colonie** : Construisez et agrandissez votre fourmilière en creusant des salles spécialisées (nurserie, dépôt...).
- **Système de tâches intelligent** : Un gestionnaire de tâches (`TaskManager`) distribue automatiquement les rôles aux fourmis disponibles (ouvrières, guerrières, nourrices, etc.).
- **Phase d'exploration** : Partez en expedition pour récupérer des ressources dans un mini jeu stratégique.
- **Sauvegarde** : L'état de la partie peut être sauvegardé et rechargé grâce au `SaveManager`.
- **Interface utilisateur sur mesure** : Tous les menus et éléments d'interface sont développés manuellement par-dessus `pygame-ce`, sans framework UI externe.

---

<a id="installation"></a>
## Installation, démarrage et prérequis

### Prérequis & versions

*A noter que ci-dessous ne sont listés que les modules nécessaire au fonctionnement unique du code. Ainsi, pour executer les tests, merci de vous référer à la séction "Tests"*

- **Python 3.8+** : Le projet est testé pour fonctionner sur cette version, mais il est **fortement recommandé** d'utiliser la dernière version stable de Python.
- **pip** : Pour l'installation des dépendances (inclus lors de l'installation de Python).
- [**pygame-ce**](https://pyga.me/) : La version communautaire de pygame, utilisée comme moteur de rendu. *Version utilisée : `pygame-ce@2.5.6`.*
- **networkx** : Bibliothèque de gestion de graphes, utilisée pour le module d'expédition. *Version utilisée : `networkx@3.4.2`.*

### Installation

Si vous installez le projet via git :

```bash
git clone https://github.com/Nexooow/projet-trophees-nsi.git
cd projet-trophees-nsi
pip install -r "requirements.txt"
```

Sinon, vous pouvez simplement ouvrir le répertoire ou se situe ce projet et executer la commande suivante;

```bash
pip install -r "requirements.txt"
```

### Démarrer le jeu

```bash
python3 sources/main.py
```

---

## Tests

Les tests sont écrits à l'aide de `pytest` et se trouvent dans le répertoire `tests/`. Pour les exécuter, utilisez la commande suivante depuis la racine du projet :

``` bash
python -m pytest tests/
```
ou simplement
``` bash
pytest tests/
```

<a id="structure"></a>
## Structure du projet

```
├── sources/
│   ├── main.py               # Point d'entrée du jeu
│   ├── constants.py          # Constantes globales
│   ├── core/                 # Moteur central
│   ├── colony/               # Logique de la fourmilière
│   └── exploration/          # Module qui gère le minijeu d'exploraiton
│
├── docs/                     # Documentation
├── tests/                    # Tests automatisés (pytest)
├── data/                     # Ressources (sprites, sons, polices et sauvegardes)
└── requirements.txt
```

---

<a id="auteurs"></a>
## 👥 Auteurs

- **SCHLEICHER Nikolaï** — Architecture du moteur, UI Manager, cycle jour/nuit, système de sauvegarde
- **DISCAZEAUX Pierre** — Module d'exploration, gestion des graphes, algorithmes de combat, gestion des unités

### Licence

Ce projet est sous licence **Apache License 2.0** — Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

### Crédits

#### Police d'écriture

[*m5x7*, par Daniel Linssen](https://managore.itch.io/m5x7)

#### Sons ambients

[*Evening Nature with Crickets, Birds and Distant Dogs – Part 2*, par Eryliaa](https://pixabay.com/sound-effects/nature-evening-nature-with-crickets-birds-and-distant-dogs-part-2-445150/)