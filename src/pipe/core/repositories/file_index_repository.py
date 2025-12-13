import hashlib
import logging
import os

from pathspec import PathSpec
from pipe.core.models.file_search import Level1Candidate, LsEntry
from whoosh.fields import BOOLEAN, ID, NUMERIC, TEXT, Schema
from whoosh.index import create_in, open_dir
from whoosh.qparser import OrGroup, QueryParser
from whoosh.query import And, Term


class FileIndexRepository:
    GITIGNORE_FILE = ".gitignore"

    def __init__(self, base_path: str = ".", index_dir: str = "./whoosh_index"):
        self.base_path = os.path.abspath(base_path)
        self.index_dir = index_dir
        self.schema = Schema(
            path=ID(stored=True, unique=True),
            filename=TEXT(stored=True),
            is_dir=BOOLEAN(stored=True),
            parent_path_hash=ID(stored=True),
            size=NUMERIC(stored=True, sortable=True),
            last_modified=NUMERIC(stored=True, sortable=True),
        )
        self.logger = logging.getLogger(__name__)
        self._ensure_index_dir()

    def _ensure_index_dir(self):
        if not os.path.exists(self.index_dir):
            try:
                os.makedirs(self.index_dir, mode=0o755)
                self.logger.info(f"Created index directory: {self.index_dir}")
            except OSError as e:
                raise RuntimeError(
                    f"Failed to create index directory {self.index_dir}: {e}"
                ) from e

    def _get_gitignore_spec(self) -> PathSpec:
        gitignore_path = os.path.join(self.base_path, self.GITIGNORE_FILE)
        patterns = []

        # Always exclude common patterns
        default_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".Python",
            "*.so",
            "*.egg-info/",
            ".git/",
            ".venv/",
            "venv/",
            "node_modules/",
            ".DS_Store",
        ]
        patterns.extend(default_patterns)

        # Add patterns from .gitignore if it exists
        if os.path.exists(gitignore_path):
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return PathSpec.from_lines("gitwildmatch", patterns)

    def _should_ignore(self, relative_path: str, gitignore_spec: PathSpec) -> bool:
        # pathspecはスラッシュで始まるパスを期待する
        if not relative_path.startswith(os.sep):
            relative_path = os.sep + relative_path
        return gitignore_spec.match_file(relative_path)

    def _get_parent_path_hash(self, full_path: str) -> str:
        parent_path = os.path.dirname(full_path)
        if not parent_path.startswith(self.base_path):
            # base_path自体が親になる場合 (例: /data/files の直下)
            return hashlib.sha256(self.base_path.encode("utf-8")).hexdigest()
        return hashlib.sha256(parent_path.encode("utf-8")).hexdigest()

    def create_index(self):
        self.logger.info(f"Creating index in {self.index_dir} for {self.base_path}")
        if not os.path.exists(self.base_path):
            raise ValueError(f"Base path does not exist: {self.base_path}")

        ix = create_in(self.index_dir, self.schema)
        writer = ix.writer()
        gitignore_spec = self._get_gitignore_spec()

        indexed_count = 0
        for root, dirs, files in os.walk(self.base_path):
            # .gitignoreで無視されるディレクトリをスキップ
            dirs[:] = [
                d
                for d in dirs
                if not self._should_ignore(
                    os.path.relpath(os.path.join(root, d), self.base_path),
                    gitignore_spec,
                )
            ]

            for name in dirs + files:
                full_path = os.path.join(root, name)
                relative_path = os.path.relpath(full_path, self.base_path)

                if self._should_ignore(relative_path, gitignore_spec):
                    continue

                is_dir = os.path.isdir(full_path)
                parent_path_hash = self._get_parent_path_hash(full_path)

                try:
                    stat_info = os.stat(full_path)
                    size = stat_info.st_size if not is_dir else None
                    last_modified = stat_info.st_mtime
                except OSError:
                    size = None
                    last_modified = None

                writer.add_document(
                    path=full_path,
                    filename=name,
                    is_dir=is_dir,
                    parent_path_hash=parent_path_hash,
                    size=size,
                    last_modified=last_modified,
                )
                indexed_count += 1
        writer.commit()
        self.logger.info(f"Indexed {indexed_count} files and directories")

    def search_l1_candidates(
        self, current_parent_path: str, query: str
    ) -> list[Level1Candidate]:
        ix = open_dir(self.index_dir)
        searcher = ix.searcher()
        current_parent_path = os.path.abspath(current_parent_path)
        parent_hash = hashlib.sha256(current_parent_path.encode("utf-8")).hexdigest()

        # filenameフィールドで部分一致検索
        # TEXT fields in Whoosh are tokenized by default, so Term queries
        # result in exact matches. For partial matches, wildcard queries
        # or custom analyzers are needed. Here, we use QueryParser to build
        # wildcard queries for partial matching, combining with Term queries
        # for parent_path_hash as instructed.

        query_terms = query.split()
        # If the query is empty, return all entries directly under the parent directory
        if not query_terms:
            q = Term("parent_path_hash", parent_hash)
        else:
            # Combine filename partial match with parent_path_hash Term query
            # Using wildcard queries for partial matching on TEXT fields.
            # Note: Wildcards can impact performance.
            parser = QueryParser("filename", schema=ix.schema, group=OrGroup)
            filename_query = parser.parse(
                " OR ".join([f"*{term}*" for term in query_terms])
            )

            parent_query = Term("parent_path_hash", parent_hash)
            q = And([parent_query, filename_query])

        results = searcher.search(q, limit=None)  # limit=Noneで全件取得
        candidates = []
        for hit in results:
            candidates.append(
                Level1Candidate(
                    name=hit["filename"],
                    is_dir=hit["is_dir"],
                    path_segment=hit["filename"],
                )
            )
        searcher.close()
        return candidates

    def get_l2_prefetched_data(
        self, parent_dir_names: list[str], current_base_path: str
    ) -> dict[str, list[Level1Candidate]]:
        ix = open_dir(self.index_dir)
        searcher = ix.searcher()
        prefetched_data = {}
        current_base_path = os.path.abspath(current_base_path)

        for dir_name in parent_dir_names:
            full_path_of_l1_dir = os.path.join(current_base_path, dir_name)
            parent_hash_for_l2 = hashlib.sha256(
                full_path_of_l1_dir.encode("utf-8")
            ).hexdigest()

            q = Term("parent_path_hash", parent_hash_for_l2)
            results = searcher.search(q, limit=None)

            l2_candidates = []
            for hit in results:
                l2_candidates.append(
                    Level1Candidate(
                        name=hit["filename"],
                        is_dir=hit["is_dir"],
                        path_segment=hit["filename"],
                    )
                )
            prefetched_data[dir_name] = l2_candidates
        searcher.close()
        return prefetched_data

    def get_ls_data(self, full_path: str) -> list[LsEntry]:
        if not os.path.exists(self.index_dir):
            raise FileNotFoundError(
                f"Index directory does not exist: {self.index_dir}. "
                "Please create the index first by calling create_index()."
            )
        try:
            ix = open_dir(self.index_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to open index at {self.index_dir}: {e}") from e
        searcher = ix.searcher()
        ls_entries = []
        full_path = os.path.abspath(full_path)

        if os.path.isdir(full_path):
            parent_hash = hashlib.sha256(full_path.encode("utf-8")).hexdigest()
            q = Term("parent_path_hash", parent_hash)
            results = searcher.search(q, limit=None)
            for hit in results:
                ls_entries.append(
                    LsEntry(
                        name=hit["filename"],
                        is_dir=hit["is_dir"],
                        size=hit["size"],
                        last_modified=hit["last_modified"],
                        path=hit["path"],
                    )
                )
        else:  # ファイルの場合、そのファイル自身の情報を返す
            q = Term("path", full_path)
            results = searcher.search(q, limit=1)
            if results:
                hit = results[0]
                ls_entries.append(
                    LsEntry(
                        name=hit["filename"],
                        is_dir=hit["is_dir"],
                        size=hit["size"],
                        last_modified=hit["last_modified"],
                        path=hit["path"],
                    )
                )
        searcher.close()
        return ls_entries
