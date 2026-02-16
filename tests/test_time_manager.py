from src.core.TimeManager import TimeManager
from unittest.mock import MagicMock

def test_time_manager_basic():
    game = MagicMock()
    game.state.is_flag_active.return_value = False
    
    tm = TimeManager(game)
    assert tm.is_paused() == True # Default is paused
    
    tm.paused = False
    assert tm.is_paused() == False
    
    game.state.is_flag_active.return_value = True
    assert tm.is_paused() == True

def test_time_manager_progression():
    game = MagicMock()
    game.state.is_flag_active.return_value = False
    tm = TimeManager(game)
    tm.paused = False
    
    tm.set_time(0)
    for _ in range(60):
        tm.add_frame()
    
    assert tm.time == 1
    assert tm.get_time() == (0, 1)

def test_is_day():
    game = MagicMock()
    tm = TimeManager(game)
    
    tm.set_time(600) # 10h00
    assert tm.is_day() == True
    
    tm.set_time(1260) # 21h00
    assert tm.is_day() == False
