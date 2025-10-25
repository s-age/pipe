import unittest
import tempfile
import shutil
import os
import json
from src.session_manager import SessionManager
from src.history_manager import HistoryManager

class TestHistoryManager(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(self.test_dir)
        self.history_manager = self.session_manager.history_manager
        self.session_id = self.session_manager.create_new_session("test_purpose", "test_background", [], False)

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_add_and_get_turn(self):
        """Test adding a turn to a session and retrieving it."""
        turn_data = {"type": "user_task", "instruction": "test instruction"}
        self.history_manager.add_turn_to_session(self.session_id, turn_data)
        
        turns = self.history_manager.get_session_turns(self.session_id)
        self.assertEqual(len(turns), 1)
        self.assertEqual(turns[0]['instruction'], "test instruction")

    def test_update_turns(self):
        """Test updating all turns in a session."""
        initial_turn = {"type": "user_task", "instruction": "initial"}
        self.history_manager.add_turn_to_session(self.session_id, initial_turn)
        
        new_turns = [
            {"type": "model_response", "content": "response 1"},
            {"type": "user_task", "instruction": "next task"}
        ]
        self.history_manager.update_turns(self.session_id, new_turns)
        
        retrieved_turns = self.history_manager.get_session_turns(self.session_id)
        self.assertEqual(len(retrieved_turns), 2)
        self.assertEqual(retrieved_turns[0]['content'], "response 1")

    def test_delete_turn(self):
        """Test deleting a specific turn."""
        turns_to_add = [
            {"type": "user_task", "instruction": "task 1"},
            {"type": "model_response", "content": "response 1"},
            {"type": "user_task", "instruction": "task 2"}
        ]
        for turn in turns_to_add:
            self.history_manager.add_turn_to_session(self.session_id, turn)
            
        self.history_manager.delete_turn(self.session_id, 1) # Delete the second turn
        
        remaining_turns = self.history_manager.get_session_turns(self.session_id)
        self.assertEqual(len(remaining_turns), 2)
        self.assertEqual(remaining_turns[0]['instruction'], "task 1")
        self.assertEqual(remaining_turns[1]['instruction'], "task 2")

if __name__ == '__main__':
    unittest.main()