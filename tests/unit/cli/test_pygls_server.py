import asyncio
from unittest.mock import MagicMock, patch

import pytest
from lsprotocol import types
from pipe.cli.pygls_server import (
    _get_document_path,
    completions,
    definition,
    did_change,
    did_open,
    hover,
    main,
    references,
)


class TestPyglsServer:
    """Unit tests for pygls_server.py."""

    @pytest.fixture
    def mock_ls(self):
        """Mock LanguageServer instance."""
        ls = MagicMock()
        ls.workspace = MagicMock()
        return ls

    def test_get_document_path(self, mock_ls):
        """Test _get_document_path helper."""
        uri = "file:///path/to/file.py"
        mock_doc = MagicMock()
        mock_doc.path = "/path/to/file.py"
        mock_ls.workspace.get_document.return_value = mock_doc

        path = _get_document_path(mock_ls, uri)
        assert path == "/path/to/file.py"
        mock_ls.workspace.get_document.assert_called_once_with(uri)

    def test_did_open(self, mock_ls):
        """Test did_open feature."""
        params = MagicMock(spec=types.DidOpenTextDocumentParams)
        params.text_document.uri = "file:///test.py"

        asyncio.run(did_open(mock_ls, params))
        mock_ls.show_message_log.assert_called_once_with(
            "Document opened: file:///test.py"
        )

    def test_did_change(self, mock_ls):
        """Test did_change feature."""
        params = MagicMock(spec=types.DidChangeTextDocumentParams)
        params.text_document.uri = "file:///test.py"

        asyncio.run(did_change(mock_ls, params))
        mock_ls.show_message_log.assert_called_once_with(
            "Document changed: file:///test.py"
        )

    @patch("pipe.cli.pygls_server._get_document_path")
    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_definition_success(self, mock_analyze, mock_get_path, mock_ls):
        """Test definition feature success case."""
        uri = "file:///test.py"
        mock_get_path.return_value = "/test.py"
        params = MagicMock(spec=types.DefinitionParams)
        params.text_document.uri = uri
        params.position = types.Position(line=1, character=5)

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "MyClass"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_analyze.return_value = {
            "classes": [{"name": "MyClass", "lineno": 10, "end_lineno": 20}],
            "functions": [],
            "variables": [],
        }

        result = asyncio.run(definition(mock_ls, params))

        assert isinstance(result, types.Location)
        assert result.uri == uri
        assert result.range.start.line == 9
        assert result.range.end.line == 19

    def test_definition_no_word(self, mock_ls):
        """Test definition feature when no word is found at position."""
        params = MagicMock(spec=types.DefinitionParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = None
        mock_ls.workspace.get_document.return_value = mock_doc

        result = asyncio.run(definition(mock_ls, params))
        assert result is None

    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_definition_error(self, mock_analyze, mock_ls):
        """Test definition feature when analysis fails."""
        params = MagicMock(spec=types.DefinitionParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "word"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_analyze.return_value = {"error": "Analysis failed"}

        result = asyncio.run(definition(mock_ls, params))
        assert result is None
        mock_ls.show_message_log.assert_called_with(
            "Error analyzing code: Analysis failed"
        )

    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_definition_not_found(self, mock_analyze, mock_ls):
        """Test definition feature when symbol is not found in analysis."""
        params = MagicMock(spec=types.DefinitionParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "Unknown"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_analyze.return_value = {
            "classes": [{"name": "Other"}],
            "functions": [],
            "variables": [],
        }

        result = asyncio.run(definition(mock_ls, params))
        assert result is None

    @patch("pipe.cli.pygls_server.py_get_type_hints")
    def test_hover_type_hints(self, mock_get_hints, mock_ls):
        """Test hover feature with type hints."""
        params = MagicMock(spec=types.HoverParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "my_func"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_get_hints.return_value = {"type_hints": {"arg1": "int", "return": "str"}}

        result = asyncio.run(hover(mock_ls, params))
        assert isinstance(result, types.Hover)
        contents = result.contents
        assert isinstance(contents, types.MarkupContent)
        assert "Type Hints for my_func" in contents.value
        assert "arg1: int" in contents.value

    @patch("pipe.cli.pygls_server.py_get_type_hints")
    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_hover_docstring(self, mock_analyze, mock_get_hints, mock_ls):
        """Test hover feature with docstring."""
        params = MagicMock(spec=types.HoverParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "MyClass"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_get_hints.return_value = {}  # No type hints
        mock_analyze.return_value = {
            "classes": [{"name": "MyClass", "docstring": "Class docstring"}],
            "functions": [],
        }

        result = asyncio.run(hover(mock_ls, params))
        assert isinstance(result, types.Hover)
        contents = result.contents
        assert isinstance(contents, types.MarkupContent)
        assert "Class docstring" in contents.value

    def test_hover_no_word(self, mock_ls):
        """Test hover feature when no word is found at position."""
        params = MagicMock(spec=types.HoverParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = None
        mock_ls.workspace.get_document.return_value = mock_doc

        result = asyncio.run(hover(mock_ls, params))
        assert result is None

    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_completions_success(self, mock_analyze, mock_ls):
        """Test completions feature success case."""
        params = MagicMock(spec=types.CompletionParams)
        params.text_document.uri = "file:///test.py"

        mock_analyze.return_value = {
            "classes": [{"name": "MyClass"}],
            "functions": [{"name": "my_func"}],
            "variables": [{"name": "my_var"}],
        }

        result = asyncio.run(completions(mock_ls, params))
        assert isinstance(result, types.CompletionList)
        labels = [item.label for item in result.items]
        assert "MyClass" in labels
        assert "my_func" in labels
        assert "my_var" in labels

    @patch("pipe.cli.pygls_server.py_analyze_code")
    def test_completions_error(self, mock_analyze, mock_ls):
        """Test completions feature when analysis fails."""
        params = MagicMock(spec=types.CompletionParams)
        params.text_document.uri = "file:///test.py"

        mock_analyze.return_value = {"error": "Analysis failed"}

        result = asyncio.run(completions(mock_ls, params))
        assert isinstance(result, types.CompletionList)
        assert len(result.items) == 0
        mock_ls.show_message_log.assert_called_with(
            "Error analyzing code for completions: Analysis failed"
        )

    @patch("pipe.cli.pygls_server.py_get_symbol_references")
    def test_references_success(self, mock_get_refs, mock_ls):
        """Test references feature success case."""
        uri = "file:///test.py"
        params = MagicMock(spec=types.ReferenceParams)
        params.text_document.uri = uri

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = "my_var"
        mock_ls.workspace.get_document.return_value = mock_doc

        mock_get_refs.return_value = {
            "references": [
                {"lineno": 5, "line_content": "my_var = 10"},
                {"lineno": 15, "line_content": "print(my_var)"},
            ]
        }

        result = asyncio.run(references(mock_ls, params))
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].range.start.line == 4
        assert result[1].range.start.line == 14

    def test_references_no_word(self, mock_ls):
        """Test references feature when no word is found at position."""
        params = MagicMock(spec=types.ReferenceParams)
        params.text_document.uri = "file:///test.py"

        mock_doc = MagicMock()
        mock_doc.word_at_position.return_value = None
        mock_ls.workspace.get_document.return_value = mock_doc

        result = asyncio.run(references(mock_ls, params))
        assert result is None

    @patch("pipe.cli.pygls_server.server.start_io")
    def test_main(self, mock_start_io):
        """Test main function."""
        main()
        mock_start_io.assert_called_once()
