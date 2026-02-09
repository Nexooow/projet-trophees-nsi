# TODO: implémenter le système de sauvegarde et de chargement de partie

class Save:
    """
    Interface pour les objets qui peuvent être sauvegardés et chargés.
    """

    def save (self) -> dict:
        """
        Renvoie un dictionnaire représentant l'état de l'objet.
        """
        class_dict = self.__dict__
        for key, value in class_dict.items()[::]:
            if key.startswith("_") or not (isinstance(value, int) or isinstance(value, float) or isinstance(value, str)):
                del class_dict[key]
        return class_dict

    def load (self, data: dict):
        """
        Charge l'état de l'objet à partir d'un dictionnaire.
        """
        for key, value in data.items():
            assert hasattr(self, key), f"Clé '{key}' non reconnue pour la classe {self.__class__.__name__}"
            assert isinstance(getattr(self, key), type(value)), f"Type de la clé '{key}' incorrect pour la classe {self.__class__.__name__}"
            setattr(self, key, value)