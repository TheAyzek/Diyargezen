"""Single metadata scan of large local source packs (not one stat per entity)."""
import os
from pathlib import Path


def source_files(root):
    pending = [Path(root)]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    pending.append(Path(entry.path))
                elif entry.is_file(follow_symlinks=False) and Path(entry.name).suffix.lower() in {'.json', '.yaml', '.yml', '.db'}:
                    yield Path(entry.path), entry.stat(follow_symlinks=False)
