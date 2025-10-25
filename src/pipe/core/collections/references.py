from collections import UserList
from typing import List, Iterator, Any, Callable, Dict
import os

from pydantic_core import core_schema

from pipe.core.models.reference import Reference
from pipe.core.utils.file import read_text_file

class ReferenceCollection(UserList):
    """
    A collection of Reference objects with custom filtering logic for prompt generation.
    """
    def __init__(self, data: List[Reference] = None):
        initialized_data = data if data is not None else []
        super().__init__(initialized_data)

    def get_for_prompt(self, project_root: str) -> Iterator[dict]:
        """
        Yields reference content for prompt generation, applying filtering rules.
        - Only the last 5 references are considered.
        - Total token count is limited to approximately 50K (200,000 characters).
        """
        MAX_REFERENCES = 5
        MAX_CHARS = 200_000

        total_chars = 0
        
        # Consider only the last 5 references, iterating from newest to oldest
        references_to_consider = self.data[-MAX_REFERENCES:]
        
        for ref in reversed(references_to_consider):
            if ref.disabled or not os.path.isfile(ref.path):
                continue

            try:
                content = read_text_file(ref.path)
                content_len = len(content)

                if total_chars + content_len > MAX_CHARS:
                    # If adding this file exceeds the limit, stop here.
                    # A more granular approach could be to truncate the file,
                    # but for now, we'll just skip the rest.
                    break
                
                total_chars += content_len
                
                yield {
                    "path": os.path.relpath(ref.path, project_root),
                    "content": content
                }
            except Exception:
                # Ignore files that can't be read
                continue

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Callable[[Any], core_schema.CoreSchema]
    ) -> core_schema.CoreSchema:
        # This defines how to validate the items within the list.
        items_schema = handler(Reference)

        # This defines a schema that validates a list of the items defined above,
        # and then converts that list into an instance of our class.
        list_to_collection_schema = core_schema.chain_schema([
            core_schema.list_schema(items_schema),
            core_schema.no_info_plain_validator_function(cls),
        ])

        return core_schema.json_or_python_schema(
            # When parsing from JSON, we expect a list that needs to be converted.
            json_schema=list_to_collection_schema,
            # When creating from Python, it could be an instance of our class already,
            # or it could be a list that needs to be converted.
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    list_to_collection_schema,
                ]
            ),
            # This defines how to serialize our class back to a JSON-compatible type (a list).
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: [r.model_dump() for r in instance.data]),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.CoreSchema, handler: Callable[[Any], Dict[str, Any]]
    ) -> Dict[str, Any]:
        json_schema = handler(core_schema)
        json_schema.update(type='array', items={"$ref": "#/definitions/Reference"})
        return json_schema
