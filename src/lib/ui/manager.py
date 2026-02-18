from __future__ import annotations

from typing import Optional

import pygame

from .button import Button
from .element import Element
from .image import Image
from .label import Label
from .panel import Panel
from .progress_bar import ProgressBar


class UIManager:
    """
    Gestionnaire central de tous les éléments d'interface.
    """

    def __init__(self, game):
        self.game = game
        self.screen: pygame.Surface = game.screen

        self.elements: dict[str, Element] = {}
        # liste des éléments triés par ordre de z-index croissant
        self.draw_order: list[str] = []

    def add(self, element: Element) -> Element:
        """
        Enregistre un élément dans le gestionnaire et le retourne (toujours pour le "chaining").
        """
        self.elements[element.id] = element
        self.sort_elements()
        return element

    def remove(self, id: str) -> None:
        """
        Supprime un élément du gestionnaire par son identifiant.
        """
        if id in self.elements:
            del self.elements[id]
            self.sort_elements()

    def get(self, id: str) -> Optional[Element]:
        """
        Retourne l'élément correspondant à l'identifiant donné, ou None.
        """
        return self.elements.get(id)

    def clear(self) -> None:
        """
        Supprime tous les éléments enregistrés.
        """
        self.elements.clear()
        self.draw_order.clear()

    def sort_elements(self) -> None:
        self.draw_order = sorted(
            self.elements.keys(),
            key=lambda eid: self.elements[eid].z_index,
        )

    def label(
        self,
        id: str,
        text: str = "",
        rect=(0, 0, 0, 0),
    ) -> Label:
        """
        Crée, enregistre et retourne un Label.
        """
        el = Label(self, id, text, rect)
        self.add(el)
        return el

    def button(
        self,
        id: str,
        text: str = "",
        rect=(0, 0, 0, 0),
    ) -> Button:
        """
        Crée, enregistre et retourne un Button.
        """
        el = Button(self, id, text, rect)
        self.add(el)
        return el

    def panel(
        self,
        id: str,
        rect=(0, 0, 0, 0),
    ) -> Panel:
        """
        Crée, enregistre et retourne un Panel.
        """
        el = Panel(self, id, rect)
        self.add(el)
        return el

    def image(
        self,
        id: str,
        surface: Optional[pygame.Surface] = None,
        rect=(0, 0, 0, 0),
    ) -> Image:
        """
        Crée, enregistre et retourne une Image.
        """
        el = Image(self, id, surface, rect)
        self.add(el)
        return el

    def progress_bar(
        self,
        id: str,
        rect=(0, 0, 0, 0),
    ) -> ProgressBar:
        """
        Crée, enregistre et retourne une ProgressBar.
        """
        el = ProgressBar(self, id, rect)
        self.add(el)
        return el

    def update(self, events: list) -> None:
        """
        Transmet les événements pygame à tous les éléments racines.
        """
        for event in events:
            if event.type in (
                pygame.MOUSEBUTTONDOWN,
                pygame.MOUSEBUTTONUP,
                pygame.MOUSEMOTION,
            ):
                for eid in self.draw_order:
                    el = self.elements[eid]
                    # On ne distribue qu'aux éléments racines ; les enfants reçoivent
                    # les événements récursivement via Element.handle_event().
                    if el.parent is None:
                        el.handle_event(event)

    def draw(self) -> None:
        """
        Dessine tous les éléments racines visibles dans l'ordre des z-index.
        """
        for eid in self.draw_order:
            el = self.elements[eid]
            if el.parent is None:
                el.draw(self.screen)

    def set_all_enabled(self, enabled: bool) -> None:
        """
        Active ou désactive tous les éléments enregistrés d'un coup.
        """
        for el in self.elements.values():
            el.set_enabled(enabled)

    def set_all_visible(self, visible: bool) -> None:
        """
        Affiche ou masque tous les éléments enregistrés d'un coup.
        """
        for el in self.elements.values():
            el.set_visible(visible)

    def __contains__(self, id: str) -> bool:
        return id in self.elements

    def __len__(self) -> int:
        return len(self.elements)
