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

def same_text(left, right):
    # Normalize line endings only; do not ignore spaces, BOMs or code changes.
    if left.suffix.lower() not in {'.py', '.md', '.txt', '.json', '.svg', '.yml', '.yaml', '.bat', '.original'}:
        return False
    try:
        a = left.read_bytes().decode('utf-8')
        b = right.read_bytes().decode('utf-8')
        return a.replace('\r\n', '\n') == b.replace('\r\n', '\n')
    except (OSError, UnicodeError):
        return False

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
    changed = sorted(p for p in common if canonical[p] != staging[p])
    line_endings_only = [p for p in changed if same_text(root / p, stage / p)]
    report = {
        'mode': 'READ ONLY - no merge or deletion',
        'canonical_files': len(canonical), 'staging_files': len(staging),
        'identical': sum(canonical[p] == staging[p] for p in common),
        'line_endings_only': line_endings_only,
        'different': [p for p in changed if p not in line_endings_only],
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
