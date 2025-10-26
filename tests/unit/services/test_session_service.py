import unittest
import os
import tempfile
import shutil
from pipe.core.services.session_service import SessionService
from pipe.core.models.settings import Settings
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn

class TestSessionService(unittest.TestCase):

    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model", "search_model": "test-model", "context_limit": 10000,
            "api_mode": "gemini-api", "language": "en", "yolo": False, "expert_mode": False, "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"}
            }
        }
        self.settings = Settings(**settings_data)
        self.session_service = SessionService(project_root=self.project_root, settings=self.settings)

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_create_new_session(self):
        """Tests the creation of a new session."""
        session_id = self.session_service.create_new_session("Purpose", "Background", [])
        self.assertIsNotNone(session_id)
        
        session = self.session_service.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.purpose, "Purpose")
        
        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection), 1)
        self.assertIn(session_id, collection)

    def test_create_session_with_parent(self):
        """Tests creating a child session with a parent."""
        parent_id = self.session_service.create_new_session("Parent", "BG", [])
        child_id = self.session_service.create_new_session("Child", "BG", [], parent_id=parent_id)
        
        self.assertTrue(child_id.startswith(f"{parent_id}/"))
        
        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection), 2)

    def test_fork_session_success(self):
        """Tests the successful forking of a session."""
        session_id = self.session_service.create_new_session("Original", "BG", [])
        session = self.session_service.get_session(session_id)
        session.turns.append(UserTaskTurn(type="user_task", instruction="First", timestamp="..."))
        session.turns.append(ModelResponseTurn(type="model_response", content="First response", timestamp="..."))
        self.session_service._save_session(session)

        forked_id = self.session_service.fork_session(session_id, fork_index=1)
        self.assertIsNotNone(forked_id)
        
        forked_session = self.session_service.get_session(forked_id)
        self.assertTrue(forked_session.purpose.startswith("Fork of: Original"))
        self.assertEqual(len(forked_session.turns), 2) # Turns up to the fork point
        self.assertEqual(forked_session.turns[1].content, "First response")

    def test_edit_session_meta(self):
        """Tests editing a session's metadata."""
        session_id = self.session_service.create_new_session("Original", "BG", [])
        new_meta = {"purpose": "Updated Purpose", "background": "Updated BG"}
        self.session_service.edit_session_meta(session_id, new_meta)
        
        session = self.session_service.get_session(session_id)
        self.assertEqual(session.purpose, "Updated Purpose")
        self.assertEqual(session.background, "Updated BG")

    def test_update_and_add_references(self):
        """Tests updating and adding references to a session."""
        session_id = self.session_service.create_new_session("RefTest", "BG", [])
        
        # Create a dummy file
        ref_path = os.path.join(self.project_root, "ref1.txt")
        with open(ref_path, "w") as f: f.write("ref content")

        # Add a reference
        self.session_service.add_references(session_id, ["ref1.txt"])
        session = self.session_service.get_session(session_id)
        self.assertEqual(len(session.references), 1)
        self.assertEqual(session.references[0].path, "ref1.txt")

        # Update references (replace all)
        from pipe.core.models.reference import Reference
        new_refs = [Reference(path="new_ref.txt", disabled=True)]
        self.session_service.update_references(session_id, new_refs)
        session = self.session_service.get_session(session_id)
        self.assertEqual(len(session.references), 1)
        self.assertEqual(session.references[0].path, "new_ref.txt")
        self.assertTrue(session.references[0].disabled)

    def test_update_and_delete_todos(self):
        """Tests updating and deleting todos in a session."""
        session_id = self.session_service.create_new_session("TodoTest", "BG", [])
        
        from pipe.core.models.todo import TodoItem
        todos = [TodoItem(title="My Todo", checked=False)]
        self.session_service.update_todos(session_id, todos)
        
        session = self.session_service.get_session(session_id)
        self.assertEqual(len(session.todos), 1)
        self.assertEqual(session.todos[0].title, "My Todo")

        self.session_service.delete_todos(session_id)
        session = self.session_service.get_session(session_id)
        self.assertIsNone(session.todos)

    def test_pool_operations(self):
        """Tests adding to, getting, and clearing the turn pool."""
        session_id = self.session_service.create_new_session("PoolTest", "BG", [])
        turn = UserTaskTurn(type="user_task", instruction="Pool task", timestamp="...")
        
        self.session_service.add_to_pool(session_id, turn)
        
        pool = self.session_service.get_pool(session_id)
        self.assertEqual(len(pool), 1)
        self.assertEqual(pool[0].instruction, "Pool task")

        cleared_pool = self.session_service.get_and_clear_pool(session_id)
        self.assertEqual(len(cleared_pool), 1)
        
        pool_after_clear = self.session_service.get_pool(session_id)
        self.assertEqual(len(pool_after_clear), 0)

    def test_delete_session(self):
        """Tests deleting a session and its children."""
        parent_id = self.session_service.create_new_session("Parent", "BG", [])
        child_id = self.session_service.create_new_session("Child", "BG", [], parent_id=parent_id)
        
        self.session_service.delete_session(parent_id)
        
        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection), 0)
        self.assertIsNone(self.session_service.get_session(parent_id))
        self.assertIsNone(self.session_service.get_session(child_id))

    def test_update_token_count(self):
        """Tests updating the token count of a session."""
        session_id = self.session_service.create_new_session("TokenTest", "BG", [])
        self.session_service.update_token_count(session_id, 1234)
        
        session = self.session_service.get_session(session_id)
        self.assertEqual(session.token_count, 1234)

    def test_fork_session_index_out_of_range(self):
        """Tests that forking with an out-of-range index raises IndexError."""
        session_id = self.session_service.create_new_session("Original", "BG", [])
        with self.assertRaises(IndexError):
            self.session_service.fork_session(session_id, fork_index=5)

    def test_fork_session_from_non_model_response_turn(self):
        """Tests that forking from a turn that is not a model_response raises ValueError."""
        session_id = self.session_service.create_new_session("Original", "BG", [])
        session = self.session_service.get_session(session_id)
        session.turns.append(UserTaskTurn(type="user_task", instruction="First", timestamp="..."))
        self.session_service._save_session(session)
        
        with self.assertRaises(ValueError):
            self.session_service.fork_session(session_id, fork_index=0)

if __name__ == '__main__':
    unittest.main()
