from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .manager import UIManager

from constants import UIColors

from .element import Element

class Panel(Element):
    """
    Conteneur rectangulaire regroupant des éléments enfants.
    """

    def __init__(self, ui: "UIManager", id: str, rect=(0, 0, 0, 0)):
        super().__init__(ui, id, rect)
        self.bg_color = UIColors.BG_DARK
        self.border_color = UIColors.BORDER
        self.border_width = 2
