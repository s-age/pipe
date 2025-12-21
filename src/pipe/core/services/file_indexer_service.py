from pipe.core.models.file_search import LsEntry, SearchL2Response
from pipe.core.repositories.file_index_repository import FileIndexRepository


class FileIndexerService:
    def __init__(self, repository: FileIndexRepository):
        self.repository = repository

    def create_index(self):
        """Creates or updates the Whoosh index."""

        self.repository.create_index()

    def search_l2_data(
        self, current_path_list: list[str], query: str
    ) -> SearchL2Response:
        """


        Searches for first-level candidates and prefetches second-level data


        based on the current path and query.


        """

        current_parent_path = self.repository.base_path

        if current_path_list:
            current_parent_path = (
                self.repository.base_path + "/" + "/".join(current_path_list)
            )

        # Search L1 candidates

        level_1_candidates = self.repository.search_l1_candidates(
            current_parent_path, query
        )

        # Extract directories from L1 candidates and prefetch L2 data

        l1_dir_names = [c.name for c in level_1_candidates if c.is_dir]

        prefetch_result = self.repository.get_l2_prefetched_data(
            l1_dir_names, current_parent_path
        )

        return SearchL2Response(
            level_1_candidates=level_1_candidates,
            level_2_prefetched=prefetch_result.data,
        )

    def get_ls_data(self, final_path_list: list[str]) -> list[LsEntry]:
        """


        Retrieves ls-like data for the finally confirmed path.


        """

        full_path = self.repository.base_path

        if final_path_list:
            full_path = self.repository.base_path + "/" + "/".join(final_path_list)

        return self.repository.get_ls_data(full_path)
