"""Read-only SHA256 comparison; never merges, deletes, or follows links.

Run: python scripts/compare_local_staging.py --staging ../ModuForge_staging
Differences require review; a successful inventory is not permission to delete.
"""
import argparse
import hashlib
import json
from pathlib import Path

SKIP = {'.git', '.venv', 'venv', '__pycache__', '.pytest_cache', 'build', 'dist'}

def inventory(root):
    files, links, errors = {}, [], []
    def visit(folder):
        try:
            children = sorted(folder.iterdir())
        except OSError as exc:
            errors.append({'path': folder.relative_to(root).as_posix(), 'error': str(exc)})
            return
        for path in children:
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                links.append(relative)
                continue
            if path.name in SKIP and path.is_dir():
                continue
            try:
                if path.is_dir():
                    visit(path)
                elif path.is_file():
                    # Read bytes only; include local databases/logs so they are not lost.
                    digest = hashlib.sha256()
                    with path.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            digest.update(block)
                    files[relative] = digest.hexdigest()
            except OSError as exc:
                errors.append({'path': relative, 'error': str(exc)})
    visit(root)
    return files, links, errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staging', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    stage = args.staging.absolute()
    if stage.is_symlink() or (hasattr(stage, 'is_junction') and stage.is_junction()):
        parser.error('Staging root must not be a link or junction')
    if not stage.is_dir() or stage.resolve() == root:
        parser.error('Choose an existing, separate staging directory')
    canonical, left_links, left_errors = inventory(root)
    staging, right_links, right_errors = inventory(stage)
    common = canonical.keys() & staging.keys()
    report = {
        'mode': 'READ ONLY - no merge or deletion',
        'canonical_files': len(canonical), 'staging_files': len(staging),
        'identical': sum(canonical[p] == staging[p] for p in common),
        'different': sorted(p for p in common if canonical[p] != staging[p]),
        'staging_only': sorted(staging.keys() - canonical.keys()),
        'canonical_only': sorted(canonical.keys() - staging.keys()),
        'excluded_directories': sorted(SKIP),
        'skipped_links': {'canonical': left_links, 'staging': right_links},
        'read_errors': {'canonical': left_errors, 'staging': right_errors},
        'decision': 'Review differences, local data and exclusions before retiring staging.'
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if left_errors or right_errors or left_links or right_links else 0

if __name__ == '__main__':
    raise SystemExit(main())
