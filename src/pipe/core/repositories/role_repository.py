import os

from pipe.core.models.role import RoleOption


class RoleRepository:
    def __init__(self, roles_root_dir: str):
        self.roles_root_dir = roles_root_dir

    def get_all_role_options(self) -> list[RoleOption]:
        role_options: list[RoleOption] = []
        for root, _, files in os.walk(self.roles_root_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    full_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(full_path, self.roles_root_dir)
                    # Remove .md extension for the label
                    label = os.path.splitext(relative_path)[0].replace(os.sep, "/")
                    value = f"roles/{relative_path.replace(os.sep, '/')}"
                    role_options.append(RoleOption(label=label, value=value))
        return sorted(role_options, key=lambda x: x.label)
