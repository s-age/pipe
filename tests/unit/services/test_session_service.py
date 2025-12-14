import os
import shutil
import tempfile
import unittest
from unittest.mock import Mock

from pipe.core.factories.service_factory import ServiceFactory
from pipe.core.models.settings import Settings
from pipe.core.models.turn import ModelResponseTurn, UserTaskTurn
from pipe.core.repositories.session_repository import SessionRepository


class TestSessionService(unittest.TestCase):
    def setUp(self):
        self.project_root = tempfile.mkdtemp()
        settings_data = {
            "model": "test-model",
            "search_model": "test-model",
            "context_limit": 10000,
            "api_mode": "gemini-api",
            "language": "en",
            "yolo": False,
            "expert_mode": False,
            "timezone": "UTC",
            "parameters": {
                "temperature": {"value": 0.5, "description": "t"},
                "top_p": {"value": 0.9, "description": "p"},
                "top_k": {"value": 40, "description": "k"},
            },
        }
        self.settings = Settings(**settings_data)

        from datetime import datetime

        from pipe.core.models.session_index import SessionIndex, SessionIndexEntry

        # In-memory session storage for testing
        self.sessions: dict = {}
        self.session_index_entries: dict[str, SessionIndexEntry] = {}

        # Create mock repository BEFORE service creation
        self.mock_repository = Mock(spec=SessionRepository)

        def save_session(session):
            self.sessions[session.session_id] = session
            # Also update the mock index entry
            self.session_index_entries[session.session_id] = SessionIndexEntry(
                created_at=session.created_at,
                last_updated_at=datetime.now(
                    self.session_service.timezone_obj
                ).isoformat(),
                purpose=session.purpose,
            )
            return session

        def find_session(session_id):
            return self.sessions.get(session_id)

        # New mock for load_index
        def load_index_mock():
            return SessionIndex(sessions=self.session_index_entries)

        def delete_session(session_id):
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_index_entries:
                del self.session_index_entries[session_id]
            # Also remove children from both stores
            children_to_delete = [
                sid for sid in self.sessions if sid.startswith(f"{session_id}/")
            ]
            for sid in children_to_delete:
                if sid in self.sessions:
                    del self.sessions[sid]
                if sid in self.session_index_entries:
                    del self.session_index_entries[sid]

        self.mock_repository.save.side_effect = save_session
        self.mock_repository.find.side_effect = find_session
        self.mock_repository.load_index.side_effect = load_index_mock
        self.mock_repository.delete.side_effect = delete_session
        self.mock_repository.backup.return_value = None  # No-op for tests

        # Mock _get_path_for_id to return a fake path
        self.mock_repository._get_path_for_id = Mock(
            side_effect=lambda sid: f"{self.project_root}/sessions/{sid}.json"
        )

        # Create service factory for proper service initialization
        self.service_factory = ServiceFactory(self.project_root, self.settings)
        self.session_service = self.service_factory.create_session_service()

        # Replace repository with mock BEFORE creating other services
        self.session_service.repository = self.mock_repository

        # Now create other services - they will create new session_service instances
        # so we need to replace their repositories too
        self.workflow_service = self.service_factory.create_session_workflow_service()
        self.workflow_service.repository = self.mock_repository

        self.reference_service = self.service_factory.create_session_reference_service()
        self.reference_service.repository = self.mock_repository

        self.todo_service = self.service_factory.create_session_todo_service()
        self.todo_service.repository = self.mock_repository

        self.meta_service = self.service_factory.create_session_meta_service()
        self.meta_service.repository = self.mock_repository

        self.turn_service = self.service_factory.create_session_turn_service()
        self.turn_service.repository = self.mock_repository

    def tearDown(self):
        shutil.rmtree(self.project_root)

    def test_create_new_session(self):
        """Tests the creation of a new session."""
        session = self.session_service.create_new_session("Purpose", "Background", [])
        self.assertIsNotNone(session)
        session_id = session.session_id

        fetched_session = self.session_service.get_session(session_id)
        self.assertIsNotNone(fetched_session)
        self.assertEqual(fetched_session.purpose, "Purpose")

        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection.sessions), 1)
        self.assertIn(session_id, collection.sessions)

    def test_create_session_with_parent(self):
        """Tests creating a child session with a parent."""
        parent_session = self.session_service.create_new_session("Parent", "BG", [])
        parent_id = parent_session.session_id
        child_session = self.session_service.create_new_session(
            "Child", "BG", [], parent_id=parent_id
        )
        child_id = child_session.session_id

        self.assertTrue(child_id.startswith(f"{parent_id}/"))

        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection.sessions), 2)

    def test_fork_session_success(self):
        """Tests the successful forking of a session."""
        session = self.session_service.create_new_session("Original", "BG", [])
        session_id = session.session_id
        session.turns.append(
            UserTaskTurn(type="user_task", instruction="First", timestamp="...")
        )
        session.turns.append(
            ModelResponseTurn(
                type="model_response", content="First response", timestamp="..."
            )
        )
        self.session_service.repository.save(session)

        forked_id = self.workflow_service.fork_session(session_id, fork_index=1)
        self.assertIsNotNone(forked_id)

        forked_session = self.session_service.get_session(forked_id)
        self.assertTrue(forked_session.purpose.startswith("Fork of: Original"))
        self.assertEqual(len(forked_session.turns), 2)  # Turns up to the fork point
        self.assertEqual(forked_session.turns[1].content, "First response")

    def test_edit_session_meta(self):
        """Tests editing a session's metadata."""
        session = self.session_service.create_new_session("Original", "BG", [])
        session_id = session.session_id
        new_meta = {"purpose": "Updated Purpose", "background": "Updated BG"}
        self.meta_service.edit_session_meta(session_id, new_meta)

        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(fetched_session.purpose, "Updated Purpose")
        self.assertEqual(fetched_session.background, "Updated BG")

    def test_update_and_add_references(self):
        """Tests updating and adding references to a session."""
        session = self.session_service.create_new_session("RefTest", "BG", [])
        session_id = session.session_id

        # Create a dummy file
        ref_path = os.path.join(self.project_root, "ref1.txt")
        with open(ref_path, "w") as f:
            f.write("ref content")

        # Add a reference
        self.reference_service.add_reference_to_session(session_id, "ref1.txt")
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertEqual(fetched_session.references[0].path, "ref1.txt")

        # Update references (replace all)
        from pipe.core.models.reference import Reference

        new_refs = [Reference(path="new_ref.txt", disabled=True)]
        self.reference_service.update_references(session_id, new_refs)
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertEqual(fetched_session.references[0].path, "new_ref.txt")
        self.assertTrue(fetched_session.references[0].disabled)

    def test_update_and_delete_todos(self):
        """Tests updating and deleting todos in a session."""
        session = self.session_service.create_new_session("TodoTest", "BG", [])
        session_id = session.session_id

        from pipe.core.models.todo import TodoItem

        todos = [TodoItem(title="My Todo", checked=False)]
        self.todo_service.update_todos(session_id, todos)

        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(len(fetched_session.todos), 1)
        self.assertEqual(fetched_session.todos[0].title, "My Todo")

        self.todo_service.delete_todos(session_id)
        fetched_session = self.session_service.get_session(session_id)
        self.assertIsNone(fetched_session.todos)

    def test_pool_operations(self):
        """Tests adding to, getting, and clearing the turn pool."""
        session = self.session_service.create_new_session("PoolTest", "BG", [])
        session_id = session.session_id
        turn = UserTaskTurn(type="user_task", instruction="Pool task", timestamp="...")

        fetched_session = self.session_service.get_session(session_id)
        fetched_session.pools.append(turn)

        # Test get_pool
        self.assertEqual(len(fetched_session.pools), 1)
        self.assertEqual(fetched_session.pools[0].instruction, "Pool task")

        # Test get_and_clear_pool
        cleared_pool = fetched_session.pools.copy()
        fetched_session.pools.clear()
        self.assertEqual(len(cleared_pool), 1)
        self.assertEqual(len(fetched_session.pools), 0)

    def test_delete_session(self):
        """Tests deleting a session and its children."""
        parent_session = self.session_service.create_new_session("Parent", "BG", [])
        parent_id = parent_session.session_id
        child_session = self.session_service.create_new_session(
            "Child", "BG", [], parent_id=parent_id
        )
        child_id = child_session.session_id

        self.session_service.delete_session(parent_id)

        collection = self.session_service.list_sessions()
        self.assertEqual(len(collection.sessions), 0)
        self.assertIsNone(self.session_service.get_session(parent_id))
        self.assertIsNone(self.session_service.get_session(child_id))

    def test_update_token_count(self):
        """Tests updating the token count of a session."""
        session = self.session_service.create_new_session("TokenTest", "BG", [])
        session_id = session.session_id
        self.meta_service.update_token_count(session_id, 1234)

        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(fetched_session.token_count, 1234)

    def test_fork_session_index_out_of_range(self):
        """Tests that forking with an out-of-range index raises IndexError."""
        session = self.session_service.create_new_session("Original", "BG", [])
        session_id = session.session_id
        with self.assertRaises(IndexError):
            self.workflow_service.fork_session(session_id, fork_index=5)

    def test_fork_session_from_non_model_response_turn(self):
        """Tests that forking from a turn that is not a model_response raises
        ValueError."""
        session = self.session_service.create_new_session("Original", "BG", [])
        session_id = session.session_id
        fetched_session = self.session_service.get_session(session_id)
        fetched_session.turns.append(
            UserTaskTurn(type="user_task", instruction="First", timestamp="...")
        )
        self.session_service.repository.save(fetched_session)

        with self.assertRaises(ValueError):
            self.workflow_service.fork_session(session_id, fork_index=0)

    def test_add_reference_to_session(self):
        """Tests that add_reference_to_session adds new but not duplicate references."""
        session = self.session_service.create_new_session("Test", "BG", [])
        session_id = session.session_id
        ref_path = os.path.join(self.project_root, "ref.txt")
        with open(ref_path, "w") as f:
            f.write("content")

        # Add new reference
        self.reference_service.add_reference_to_session(session_id, "ref.txt")
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(len(fetched_session.references), 1)
        self.assertEqual(fetched_session.references[0].path, "ref.txt")
        self.assertEqual(fetched_session.references[0].ttl, 3)

        # Try to add the same reference again
        self.reference_service.add_reference_to_session(session_id, "ref.txt")
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(len(fetched_session.references), 1)  # Should not add duplicate

    def test_update_reference_ttl_in_session(self):
        """Tests updating the TTL for a reference."""
        session = self.session_service.create_new_session("Test", "BG", [])
        session_id = session.session_id
        ref_path = os.path.join(self.project_root, "ref.txt")
        with open(ref_path, "w") as f:
            f.write("content")
        self.reference_service.add_reference_to_session(session_id, "ref.txt")

        # Update TTL
        self.reference_service.update_reference_ttl_in_session(session_id, "ref.txt", 5)
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(fetched_session.references[0].ttl, 5)
        self.assertFalse(fetched_session.references[0].disabled)

        # Update TTL to 0
        self.reference_service.update_reference_ttl_in_session(session_id, "ref.txt", 0)
        fetched_session = self.session_service.get_session(session_id)
        self.assertEqual(fetched_session.references[0].ttl, 0)
        self.assertTrue(fetched_session.references[0].disabled)

    def test_save_session_sorts_references(self):
        """Tests that repository.save correctly sorts references by TTL."""
        from pipe.core.collections.references import ReferenceCollection
        from pipe.core.models.reference import Reference

        session = self.session_service.create_new_session("Test", "BG", [])
        session_id = session.session_id
        fetched_session = self.session_service.get_session(session_id)
        fetched_session.references = ReferenceCollection(
            [
                Reference(path="ref1.txt", disabled=False, ttl=2),
                Reference(path="ref2.txt", disabled=True, ttl=5),
                Reference(path="ref3.txt", disabled=False, ttl=None),  # treated as 3
                Reference(path="ref4.txt", disabled=False, ttl=5),
            ]
        )
        self.session_service.repository.save(fetched_session)

        # Re-fetch and check order
        saved_session = self.session_service.get_session(session_id)
        paths = [ref.path for ref in saved_session.references]
        expected_order = ["ref4.txt", "ref3.txt", "ref1.txt", "ref2.txt"]
        self.assertEqual(paths, expected_order)

    def test_prepare_session_for_takt_dry_run(self):
        """Tests that prepare does not add a turn in dry_run mode."""
        from pipe.core.models.args import TaktArgs

        args = TaktArgs(purpose="Test", background="BG", instruction="Dry run task")

        # Call with is_dry_run = True
        self.session_service.prepare(args, is_dry_run=True)
        session = self.session_service.current_session

        # The session is created, but the initial turn is NOT added
        self.assertEqual(len(session.turns), 0)

    def test_merge_pool_into_turns(self):
        """Tests that merge_pool_into_turns correctly moves turns from pool to turns
        list."""
        from pipe.core.models.turn import FunctionCallingTurn, ToolResponseTurn

        session = self.session_service.create_new_session("MergeTest", "BG", [])
        session_id = session.session_id
        fetched_session = self.session_service.get_session(session_id)

        # Add some turns to the pool
        pool_turns = [
            FunctionCallingTurn(
                type="function_calling", response="call1", timestamp="..."
            ),
            ToolResponseTurn(
                type="tool_response",
                name="tool1",
                response={
                    "status": "succeeded",
                    "message": "Tool executed successfully",
                },
                timestamp="...",
            ),
        ]
        fetched_session.pools.extend(pool_turns)

        # Verify pool is populated and turns is empty
        self.assertEqual(len(fetched_session.pools), 2)
        self.assertEqual(len(fetched_session.turns), 0)

        # Perform the merge
        fetched_session.turns.extend(fetched_session.pools)
        fetched_session.pools.clear()

        # Verify pool is cleared and turns are populated
        self.assertEqual(len(fetched_session.pools), 0)
        self.assertEqual(len(fetched_session.turns), 2)
        self.assertEqual(fetched_session.turns[0].type, "function_calling")
        self.assertEqual(fetched_session.turns[1].name, "tool1")


if __name__ == "__main__":
    unittest.main()
