import os
import pytest
from src.memory.manager import MemoryManager

def test_memory_manager_integration(tmp_path):
    db_file = tmp_path / "test_app.db"
    manager = MemoryManager(str(db_file))
    
    # Check initial profile
    assert manager.get_user_profile("session_1") == ""
    
    # Record some feedback
    manager.record_feedback("session_1", "trace_1", "Rest A", "Italian", "High", True)
    manager.record_feedback("session_1", "trace_2", "Rest B", "Italian", "High", True)
    manager.record_feedback("session_1", "trace_3", "Rest C", "Chinese", "Low", False)
    
    profile = manager.get_user_profile("session_1")
    
    # Should say affinity for Italian, High budget
    assert "Italian" in profile
    assert "High" in profile
    
    # Check a different session
    assert manager.get_user_profile("session_2") == ""
