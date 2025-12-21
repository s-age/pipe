import logging
from collections import UserList
from collections.abc import Callable
from typing import Any

from pipe.core.models.reference import Reference
from pydantic_core import core_schema

logger = logging.getLogger(__name__)


class ReferenceCollection(UserList):
    def __init__(self, data: list | None = None, default_ttl: int = 3):
        initialized_data = data if data is not None else []
        super().__init__(initialized_data)
        self.default_ttl = default_ttl
        self._sort_by_ttl()

    def add(self, path: str):
        if not any(ref.path == path for ref in self.data):
            self.data.append(Reference(path=path, disabled=False, ttl=self.default_ttl))
            self._sort_by_ttl()

    def update_ttl(self, path: str, new_ttl: int):
        for ref in self.data:
            if ref.path == path:
                ref.ttl = new_ttl
                ref.disabled = new_ttl <= 0
                break
        self._sort_by_ttl()

    def _sort_by_ttl(self):
        """Internal method to maintain sort order after mutations."""
        self.data.sort(
            key=lambda ref: (
                not ref.disabled,
                ref.ttl if ref.ttl is not None else self.default_ttl,
            ),
            reverse=True,
        )

    def get_for_prompt(self, resource_repository, project_root: str):
        """Get references with content for prompt generation.

        DEPRECATED: This method should be replaced with direct factory usage.
        References should be processed in the factory layer, not in collections.
        """
        import os

        from pipe.core.domains.references import get_active_references

        active_refs = get_active_references(self)
        for ref in active_refs:
            try:
                full_path = os.path.abspath(os.path.join(project_root, ref.path))
                if os.path.commonpath([project_root]) != os.path.commonpath(
                    [project_root, full_path]
                ):
                    logger.warning(
                        f"Reference path '{ref.path}' is outside the project root. "
                        "Skipping."
                    )
                    continue

                content = resource_repository.read_text(full_path, project_root)
                if content is not None:
                    yield {"path": ref.path, "content": content}
                else:
                    logger.warning(
                        f"Reference file not found or could not be read: {full_path}"
                    )
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Could not process reference file {ref.path}: {e}")
            except Exception as e:
                logger.warning(f"Could not process reference file {ref.path}: {e}")

    def decrement_all_ttl(self):
        """Decrement TTL for all non-disabled references.

        This delegates to the domain function for business logic.
        """
        from pipe.core.domains.references import decrement_all_references_ttl

        decrement_all_references_ttl(self)

    def sort_by_ttl(self):
        """Sort references by TTL (public method for backward compatibility)."""
        self._sort_by_ttl()

    def update_ttl_by_index(self, index: int, new_ttl: int):
        """Update TTL of a reference by index with validation.

        Args:
            index: Zero-based reference index
            new_ttl: New TTL value

        Raises:
            IndexError: If reference index out of range
        """
        if not (0 <= index < len(self.data)):
            raise IndexError(
                f"Reference index {index} out of range (0-{len(self.data)-1})."
            )
        self.data[index].ttl = new_ttl
        self.data[index].disabled = new_ttl <= 0
        self._sort_by_ttl()

    def update_persist_by_index(self, index: int, persist: bool):
        """Update persist state of a reference by index with validation.

        Args:
            index: Zero-based reference index
            persist: New persist state

        Raises:
            IndexError: If reference index out of range
        """
        if not (0 <= index < len(self.data)):
            raise IndexError(
                f"Reference index {index} out of range (0-{len(self.data)-1})."
            )
        self.data[index].persist = persist
        self._sort_by_ttl()

    def toggle_disabled_by_index(self, index: int) -> bool:
        """Toggle disabled state of a reference by index with validation.

        Args:
            index: Zero-based reference index

        Returns:
            New disabled state after toggle

        Raises:
            IndexError: If reference index out of range
        """
        if not (0 <= index < len(self.data)):
            raise IndexError(
                f"Reference index {index} out of range (0-{len(self.data)-1})."
            )
        self.data[index].disabled = not self.data[index].disabled
        self._sort_by_ttl()
        return self.data[index].disabled

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # Pydantic framework requirement (checklist 5-4)
        handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        reference_schema = handler(Reference)
        items_schema = core_schema.list_schema(reference_schema)
        list_to_collection_schema = core_schema.chain_schema(
            [
                items_schema,
                core_schema.no_info_plain_validator_function(cls),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=list_to_collection_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(cls),
                    list_to_collection_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: [t.model_dump() for t in instance]
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        # Pydantic framework requirement (checklist 5-4)
        handler: Callable[[Any], dict[str, Any]],
    ) -> dict[str, Any]:  # Pydantic framework requirement (checklist 5-4)
        # handler(core_schema) will generate the schema for the inner items
        # and add them to the definitions.
        field_schema = handler(core_schema)

        # Then we can reference the schema for the inner items.
        return {"type": "array", "items": field_schema.get("items")}
