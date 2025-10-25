import unittest
from pipe.core.models.session import Session
from pipe.core.models.reference import Reference
from pipe.core.models.todo import TodoItem
from pipe.core.collections.turns import TurnCollection

class TestSessionModel(unittest.TestCase):

    def test_session_creation_from_dict(self):
        """
        Tests that a Session object can be correctly created from a dictionary,
        simulating data loaded from a JSON file.
        """
        session_data = {
            "session_id": "test-session-123",
            "created_at": "2025-10-26T10:00:00Z",
            "purpose": "Test the Session model",
            "background": "This is a test.",
            "roles": ["roles/engineer.md"],
            "references": [
                {"path": "src/main.py", "disabled": False}
            ],
            "todos": [
                {"title": "Write test", "description": "", "checked": True}
            ]
        }
        
        session = Session(**session_data)
        
        self.assertEqual(session.session_id, "test-session-123")
        self.assertEqual(session.purpose, "Test the Session model")
        self.assertEqual(len(session.references), 1)
        self.assertIsInstance(session.references[0], Reference)
        self.assertEqual(session.references[0].path, "src/main.py")
        self.assertEqual(len(session.todos), 1)
        self.assertIsInstance(session.todos[0], TodoItem)
        self.assertEqual(session.todos[0].title, "Write test")
        self.assertTrue(session.todos[0].checked)

    def test_session_serialization_to_dict(self):
        """
        Tests that the to_dict() method produces a serializable dictionary
        with the correct structure and data.
        """
        session = Session(
            session_id="test-session-456",
            created_at="2025-10-26T11:00:00Z",
            purpose="Test serialization",
            references=[Reference(path="README.md", disabled=False)],
            todos=[TodoItem(title="Deploy", description="", checked=False)]
        )
        
        session_dict = session.to_dict()
        
        self.assertEqual(session_dict['session_id'], "test-session-456")
        self.assertEqual(session_dict['purpose'], "Test serialization")
        self.assertEqual(len(session_dict['references']), 1)
        self.assertEqual(session_dict['references'][0]['path'], "README.md")
        self.assertEqual(len(session_dict['todos']), 1)
        self.assertEqual(session_dict['todos'][0]['title'], "Deploy")

    def test_default_factories(self):
        """
        Tests that fields with default factories (like turns and references)
        are initialized correctly for a new session.
        """
        session = Session(
            session_id="new-session",
            created_at="2025-10-26T12:00:00Z"
        )
        self.assertEqual(session.references, [])
        self.assertIsInstance(session.turns, TurnCollection)
        self.assertEqual(len(session.turns), 0)
        self.assertIsNone(session.todos)

if __name__ == '__main__':
    unittest.main()
