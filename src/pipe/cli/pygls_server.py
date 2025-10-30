import os
import sys

from lsprotocol import types
from lsprotocol.types import (
    CompletionItem,
    CompletionList,
    Hover,
    Location,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
)
from pygls.server import LanguageServer

# Add src directory to Python path BEFORE local imports
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

# Import the custom tools
from pipe.core.tools.py_analyze_code import py_analyze_code
from pipe.core.tools.py_get_symbol_references import py_get_symbol_references
from pipe.core.tools.py_get_type_hints import py_get_type_hints

# Initialize the Language Server
server = LanguageServer("pipe-pygls-server", "v0.1")


def _get_document_path(ls: LanguageServer, uri: str) -> str:
    """
    Helper function to get the absolute file path from a document URI.
    """
    return ls.workspace.get_document(uri).path


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LanguageServer, params: types.DidOpenTextDocumentParams):
    ls.show_message_log(f"Document opened: {params.text_document.uri}")


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
async def did_change(ls: LanguageServer, params: types.DidChangeTextDocumentParams):
    ls.show_message_log(f"Document changed: {params.text_document.uri}")


@server.feature(types.TEXT_DOCUMENT_DEFINITION)
async def definition(
    ls: LanguageServer, params: types.DefinitionParams
) -> Location | list[Location] | None:
    file_path = _get_document_path(ls, params.text_document.uri)

    # ここでは簡易的に、カーソル位置の単語をシンボル名として扱う
    # 実際のLSPではASTを解析して正確なシンボルを特定する必要がある
    document = ls.workspace.get_document(params.text_document.uri)
    word = document.word_at_position(params.position)

    if not word:
        return None

    analysis_result = py_analyze_code(file_path)
    if "error" in analysis_result:
        ls.show_message_log(f"Error analyzing code: {analysis_result['error']}")
        return None

    for symbol_type in ["classes", "functions", "variables"]:
        for symbol in analysis_result[symbol_type]:
            if symbol["name"] == word:
                return Location(
                    uri=params.text_document.uri,
                    range=Range(
                        start=Position(line=symbol["lineno"] - 1, character=0),
                        end=Position(line=symbol["end_lineno"] - 1, character=0),
                    ),
                )
    return None


@server.feature(types.TEXT_DOCUMENT_HOVER)
async def hover(ls: LanguageServer, params: types.HoverParams) -> Hover | None:
    file_path = _get_document_path(ls, params.text_document.uri)
    document = ls.workspace.get_document(params.text_document.uri)
    word = document.word_at_position(params.position)

    if not word:
        return None

    type_hints_result = py_get_type_hints(file_path, word)
    if "type_hints" in type_hints_result:
        content = f"""```python
# Type Hints for {word}:
"""
        for name, hint in type_hints_result["type_hints"].items():
            content += f"#   {name}: {hint}\n"
        content += "```"
        return Hover(
            contents=MarkupContent(kind=MarkupKind.Markdown, value=content)
        )

    analysis_result = py_analyze_code(file_path)
    if "error" not in analysis_result:
        for symbol_type in ["classes", "functions"]:
            for symbol in analysis_result[symbol_type]:
                if symbol["name"] == word and symbol["docstring"]:
                    return Hover(
                        contents=MarkupContent(
                            kind=MarkupKind.Markdown,
                            value=f"""```python
{symbol["docstring"]}
```""",
                        )
                    )

    return None


@server.feature(types.TEXT_DOCUMENT_COMPLETION)
async def completions(
    ls: LanguageServer, params: types.CompletionParams
) -> CompletionList:
    file_path = _get_document_path(ls, params.text_document.uri)
    analysis_result = py_analyze_code(file_path)
    if "error" in analysis_result:
        ls.show_message_log(
            f"Error analyzing code for completions: {analysis_result['error']}"
        )
        return CompletionList(is_incomplete=False, items=[])

    items = []
    for symbol_type in ["classes", "functions", "variables"]:
        for symbol in analysis_result[symbol_type]:
            items.append(CompletionItem(label=symbol["name"]))  # type: ignore

    return CompletionList(is_incomplete=False, items=items)


@server.feature(types.TEXT_DOCUMENT_REFERENCES)
async def references(
    ls: LanguageServer, params: types.ReferenceParams
) -> list[Location] | None:
    file_path = _get_document_path(ls, params.text_document.uri)
    document = ls.workspace.get_document(params.text_document.uri)
    word = document.word_at_position(params.position)

    if not word:
        return None

    references_result = py_get_symbol_references(file_path, word)
    if "references" in references_result:
        locations = []
        for ref in references_result["references"]:
            locations.append(
                Location(
                    uri=params.text_document.uri,
                    range=Range(
                        start=Position(line=ref["lineno"] - 1, character=0),
                        end=Position(
                            line=ref["lineno"] - 1,
                            character=len(ref["line_content"]),
                        ),  # type: ignore
                    ),
                )
            )
        return locations

    return None


def main():
    server.start_io()


if __name__ == "__main__":
    main()
