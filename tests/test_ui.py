from unittest.mock import MagicMock

import pygame
import pytest

from sources.lib.ui.element import Element
from sources.lib.ui.manager import UIManager


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.display.init()
    yield
    pygame.display.quit()


class TestUI:
    def test_element_hierarchy(self):
        ui_manager = MagicMock(spec=UIManager)
        parent = Element(ui_manager, "parent", (10, 10, 100, 100))
        child = Element(ui_manager, "child", (5, 5, 20, 20))

        parent.add_child(child)

        assert child.parent == parent
        assert child in parent.children

        # Test absolute rect calculation
        abs_rect = child.get_absolute_rect()
        assert abs_rect.x == 15  # 10 + 5
        assert abs_rect.y == 15  # 10 + 5
        assert abs_rect.width == 20
        assert abs_rect.height == 20

    def test_element_visibility_and_enabled(self):
        ui_manager = MagicMock(spec=UIManager)
        el = Element(ui_manager, "test", (0, 0, 10, 10))

        assert el.visible is True
        el.set_visible(False)
        assert el.visible is False
        el.toggle_visible()
        assert el.visible is True

        child = Element(ui_manager, "child", (0, 0, 5, 5))
        el.add_child(child)

        assert child.enabled is True
        el.set_enabled(False)
        assert el.enabled is False
        assert child.enabled is False

    def test_element_callbacks(self):
        ui_manager = MagicMock(spec=UIManager)
        el = Element(ui_manager, "test", (0, 0, 100, 100))

        click_called = False

        def on_click():
            nonlocal click_called
            click_called = True

        el.on("click", on_click)

        # Simuler un clic à (50, 50) - à l'intérieur
        event_inside = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (50, 50)}
        )
        el.handle_event(event_inside)
        assert click_called is True

        # Réinitialiser et simuler un clic à (150, 150) - à l'extérieur
        click_called = False
        event_outside = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (150, 150)}
        )
        el.handle_event(event_outside)
        assert click_called is False

    def test_element_hover(self):
        ui_manager = MagicMock(spec=UIManager)
        el = Element(ui_manager, "test", (0, 0, 100, 100))

        hover_enter = MagicMock()
        hover_leave = MagicMock()

        el.on("hover_enter", hover_enter)
        el.on("hover_leave", hover_leave)

        # Enter
        event_move_in = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (50, 50)})
        el.handle_event(event_move_in)
        assert el.hovered is True
        hover_enter.assert_called_once()

        # Stay inside
        el.handle_event(event_move_in)
        assert hover_enter.call_count == 1  # Ne doit pas être rappelé si déjà survolé

        # Leave
        event_move_out = pygame.event.Event(pygame.MOUSEMOTION, {"pos": (150, 150)})
        el.handle_event(event_move_out)
        assert el.hovered is False
        hover_leave.assert_called_once()

    def test_element_styling(self):
        ui_manager = MagicMock(spec=UIManager)
        el = Element(ui_manager, "test")

        el.set_bg_color("#FF0000")
        assert el.bg_color == (255, 0, 0, 255)

        el.set_alpha(128)
        assert el.alpha == 128

        el.set_border((0, 255, 0), 5)
        assert el.border_color == (0, 255, 0)
        assert el.border_width == 5
