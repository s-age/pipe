import os

from pipe.core.models.procedure import ProcedureOption


class ProcedureRepository:
    def __init__(self, procedures_root_dir: str):
        self.procedures_root_dir = procedures_root_dir

    def get_all_procedure_options(self) -> list[ProcedureOption]:
        procedure_options: list[ProcedureOption] = []
        for root, _, files in os.walk(self.procedures_root_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    full_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(full_path, self.procedures_root_dir)
                    # Remove .md extension for the label
                    label = os.path.splitext(relative_path)[0].replace(os.sep, "/")
                    value = f"procedures/{relative_path.replace(os.sep, '/')}"
                    procedure_options.append(ProcedureOption(label=label, value=value))
        return sorted(procedure_options, key=lambda x: x.label)