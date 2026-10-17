"""Install the reviewed checksum fix without editing model calculations.

Save this file in the project's scripts/ directory and run:
    python -B scripts/prepare_checksum_fix.py
Use --dry-run to preview the planned changes. Existing files are backed up
outside the project. Unexpected generator versions or conflicting new files
are rejected before any project file is written.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import tempfile


ORIGINAL_SOURCE = "\"\"\"Generate SHA-256 checksums for reproducibility-critical project files.\"\"\"\n\nfrom __future__ import annotations\n\nimport hashlib\nfrom pathlib import Path\n\n\nPROJECT_ROOT = Path(__file__).resolve().parents[1]\nOUTPUT_PATH = PROJECT_ROOT / \"CHECKSUMS.sha256\"\n\nROOT_FILES = (\n    \".gitignore\",\n    \"CHANGELOG.md\",\n    \"CITATION.cff\",\n    \"LICENSE\",\n    \"README.md\",\n    \"environment.yml\",\n    \"project_checkpoint.json\",\n    \"pyproject.toml\",\n    \"requirements.txt\",\n    \"start_jupyterlab.bat\",\n)\n\nFILE_PATTERNS = (\n    \".github/workflows/*.yml\",\n    \".github/workflows/*.yaml\",\n    \"data/processed/*.csv\",\n    \"data/processed/*.json\",\n    \"docs/*.md\",\n    \"docs/sources/*\",\n    \"notebooks/*.ipynb\",\n    \"scripts/*.py\",\n    \"src/**/*.py\",\n    \"tests/*.py\",\n)\n\nEXCLUDED_DIRECTORY_NAMES = {\n    \".ipynb_checkpoints\",\n    \"__pycache__\",\n}\n\n\ndef calculate_sha256(path: Path) -> str:\n    \"\"\"Return the SHA-256 digest of a file.\"\"\"\n\n    digest = hashlib.sha256()\n\n    with path.open(\"rb\") as file_handle:\n        for chunk in iter(\n            lambda: file_handle.read(1024 * 1024),\n            b\"\",\n        ):\n            digest.update(chunk)\n\n    return digest.hexdigest()\n\n\ndef collect_project_files() -> list[Path]:\n    \"\"\"Collect reproducibility-critical files deterministically.\"\"\"\n\n    selected_files: set[Path] = set()\n\n    for filename in ROOT_FILES:\n        path = PROJECT_ROOT / filename\n\n        if path.is_file():\n            selected_files.add(path)\n\n    for pattern in FILE_PATTERNS:\n        for path in PROJECT_ROOT.glob(pattern):\n            if not path.is_file():\n                continue\n\n            relative_path = path.relative_to(PROJECT_ROOT)\n\n            if any(\n                part in EXCLUDED_DIRECTORY_NAMES\n                for part in relative_path.parts\n            ):\n                continue\n\n            selected_files.add(path)\n\n    return sorted(\n        selected_files,\n        key=lambda path: path.relative_to(\n            PROJECT_ROOT\n        ).as_posix(),\n    )\n\n\ndef main() -> int:\n    \"\"\"Write the deterministic checksum manifest.\"\"\"\n\n    project_files = collect_project_files()\n\n    lines = [\n        (\n            f\"{calculate_sha256(path)}  \"\n            f\"{path.relative_to(PROJECT_ROOT).as_posix()}\"\n        )\n        for path in project_files\n    ]\n\n    OUTPUT_PATH.write_text(\n        \"\\n\".join(lines) + \"\\n\",\n        encoding=\"utf-8\",\n        newline=\"\\n\",\n    )\n\n    print(\n        f\"Wrote {len(project_files)} SHA-256 checksums \"\n        f\"to {OUTPUT_PATH}\"\n    )\n\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"

PAYLOADS = {
  "scripts/generate_checksums.py": "\"\"\"Hash the staged Git contents of reproducibility-critical project files.\n\nStage intended inputs first. Generate, stage CHECKSUMS.sha256, then run\nthis script with --check. Digests describe stored Git blob contents,\nnot the LF/CRLF presentation of files in a working directory.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport fnmatch\nimport hashlib\nimport os\nfrom pathlib import Path, PurePosixPath\nimport re\nimport shutil\nimport subprocess\nimport sys\nimport tempfile\n\n\nPROJECT_ROOT = Path(__file__).resolve().parents[1]\nMANIFEST_NAME = \"CHECKSUMS.sha256\"\nROOT_FILES = (\n    \".gitattributes\", \".gitignore\", \"CHANGELOG.md\", \"CITATION.cff\", \"LICENSE\",\n    \"README.md\", \"environment.yml\", \"project_checkpoint.json\", \"pyproject.toml\",\n    \"requirements.txt\", \"start_jupyterlab.bat\",\n)\nFILE_PATTERNS = (\n    \".github/workflows/*.yml\", \".github/workflows/*.yaml\",\n    \"data/processed/*.csv\", \"data/processed/*.json\", \"docs/*.md\",\n    \"docs/sources/*\", \"notebooks/*.ipynb\", \"scripts/*.py\", \"src/**/*.py\",\n    \"tests/*.py\",\n)\nEXCLUDED_DIRECTORY_NAMES = {\".ipynb_checkpoints\", \"__pycache__\"}\n\n\ndef find_git() -> str:\n    \"\"\"Find Git on PATH or in standard Windows Git/Desktop installations.\"\"\"\n    located = shutil.which(\"git\")\n    if located:\n        return located\n    if os.name == \"nt\":\n        candidates = []\n        for key in (\"ProgramFiles\", \"ProgramFiles(x86)\"):\n            if os.environ.get(key):\n                candidates.append(Path(os.environ[key]) / \"Git/cmd/git.exe\")\n        if os.environ.get(\"LOCALAPPDATA\"):\n            local = Path(os.environ[\"LOCALAPPDATA\"])\n            candidates.append(local / \"Programs/Git/cmd/git.exe\")\n            desktop = local / \"GitHubDesktop\"\n            candidates.extend(sorted(\n                desktop.glob(\"app-*/resources/app/git/cmd/git.exe\"),\n                reverse=True,\n            ))\n        for candidate in candidates:\n            if candidate.is_file():\n                return str(candidate)\n    raise ValueError(\"Git could not be found. Run from a terminal with Git available.\")\n\n\ndef git_bytes(git: str, *args: str, optional: bool = False) -> bytes:\n    result = subprocess.run(\n        [git, \"-C\", str(PROJECT_ROOT), *args],\n        stdout=subprocess.PIPE, stderr=subprocess.PIPE,\n        env={**os.environ, \"GIT_OPTIONAL_LOCKS\": \"0\"},\n    )\n    if result.returncode and not optional:\n        message = result.stderr.decode(\"utf-8\", errors=\"replace\").strip()\n        raise ValueError(f\"Git failed: {message}\")\n    return b\"\" if result.returncode else result.stdout\n\n\ndef matches_parts(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:\n    if not pattern:\n        return not parts\n    if pattern[0] == \"**\":\n        return matches_parts(parts, pattern[1:]) or (\n            bool(parts) and matches_parts(parts[1:], pattern)\n        )\n    return bool(parts) and fnmatch.fnmatchcase(parts[0], pattern[0]) and (\n        matches_parts(parts[1:], pattern[1:])\n    )\n\n\ndef eligible(name: str) -> bool:\n    parts = PurePosixPath(name).parts\n    if any(part in EXCLUDED_DIRECTORY_NAMES for part in parts):\n        return False\n    return name in ROOT_FILES or any(\n        matches_parts(parts, PurePosixPath(pattern).parts)\n        for pattern in FILE_PATTERNS\n    )\n\n\ndef decode_paths(data: bytes) -> set[str]:\n    return {part.decode(\"utf-8\") for part in data.split(b\"\\0\") if part}\n\n\ndef read_index(git: str) -> dict[str, tuple[str, str]]:\n    entries = {}\n    for record in git_bytes(git, \"ls-files\", \"--stage\", \"-z\").split(b\"\\0\"):\n        if not record:\n            continue\n        metadata, raw_name = record.split(b\"\\t\", 1)\n        mode, oid, stage = metadata.decode(\"ascii\").split()\n        name = raw_name.decode(\"utf-8\")\n        if not eligible(name) and name != MANIFEST_NAME:\n            continue\n        if stage != \"0\":\n            raise ValueError(f\"Resolve the merge conflict first: {name}\")\n        if mode not in {\"100644\", \"100755\"}:\n            raise ValueError(f\"Expected a regular tracked file: {name} (mode {mode})\")\n        if any(c in name for c in \"\\r\\n\\\\\"):\n            raise ValueError(f\"Unsupported manifest pathname: {name!r}\")\n        entries[name] = (mode, oid)\n    return entries\n\n\ndef validate_inputs(git: str, entries: dict, check: bool) -> None:\n    if not entries:\n        raise ValueError(\"No staged project inputs were found.\")\n    required = set(entries) - {MANIFEST_NAME}\n    missing = sorted(name for name in required if not (PROJECT_ROOT / name).is_file())\n    unstaged = decode_paths(git_bytes(\n        git, \"diff\", \"--no-ext-diff\", \"--name-only\", \"-z\", \"--\",\n    ))\n    relevant = required | ({MANIFEST_NAME} if check else set())\n    changed = sorted(unstaged & relevant)\n    untracked = sorted(name for name in decode_paths(git_bytes(\n        git, \"ls-files\", \"--others\", \"--exclude-standard\", \"-z\",\n    )) if eligible(name))\n    problems = []\n    if missing:\n        problems.append(\"Missing tracked inputs:\\n  \" + \"\\n  \".join(missing))\n    if changed:\n        problems.append(\"Stage the intended edits/deletions first:\\n  \" + \"\\n  \".join(changed))\n    if untracked:\n        problems.append(\"Review and stage these new inputs first:\\n  \" + \"\\n  \".join(untracked))\n    if problems:\n        raise ValueError(\"\\n\".join(problems))\n    if not required:\n        raise ValueError(\"No staged project inputs were found.\")\n\n\ndef hash_blobs(git: str, entries: dict) -> dict[str, str]:\n    \"\"\"Stream raw blob bytes without applying working-tree filters.\"\"\"\n    hashes = {}\n    with tempfile.TemporaryFile() as errors:\n        process = subprocess.Popen(\n            [git, \"-C\", str(PROJECT_ROOT), \"cat-file\", \"--batch\"],\n            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=errors,\n            env={**os.environ, \"GIT_OPTIONAL_LOCKS\": \"0\"},\n        )\n        try:\n            for name in sorted(set(entries) - {MANIFEST_NAME}):\n                oid = entries[name][1]\n                process.stdin.write(oid.encode(\"ascii\") + b\"\\n\")\n                process.stdin.flush()\n                header = process.stdout.readline().split()\n                if len(header) != 3 or header[0].decode(\"ascii\") != oid or header[1] != b\"blob\":\n                    raise ValueError(f\"Cannot read the staged blob: {name}\")\n                remaining = int(header[2])\n                digest = hashlib.sha256()\n                prefix = b\"\"\n                while remaining:\n                    chunk = process.stdout.read(min(1024 * 1024, remaining))\n                    if not chunk:\n                        raise ValueError(f\"Truncated Git blob: {name}\")\n                    if len(prefix) < 128:\n                        prefix += chunk[:128 - len(prefix)]\n                    digest.update(chunk)\n                    remaining -= len(chunk)\n                if process.stdout.read(1) != b\"\\n\":\n                    raise ValueError(f\"Invalid Git batch response: {name}\")\n                if prefix.startswith(b\"version https://git-lfs.github.com/spec/v1\\n\"):\n                    raise ValueError(f\"LFS pointers need a separate artifact checksum policy: {name}\")\n                hashes[name] = digest.hexdigest()\n            process.stdin.close()\n            if process.wait(timeout=30):\n                errors.seek(0)\n                raise ValueError(errors.read().decode(\"utf-8\", errors=\"replace\"))\n        finally:\n            if process.poll() is None:\n                process.kill()\n                process.wait()\n            if not process.stdin.closed:\n                process.stdin.close()\n            process.stdout.close()\n    return hashes\n\n\ndef manifest_paths(data: bytes) -> set[str]:\n    result = set()\n    for line in data.decode(\"utf-8-sig\").splitlines():\n        if not line:\n            continue\n        match = re.fullmatch(r\"[0-9a-f]{64}  (.+)\", line)\n        if not match or match[1] in result:\n            raise ValueError(\"The previous manifest contains an invalid or duplicate entry.\")\n        result.add(match[1])\n    return result\n\n\ndef report_inventory(git: str, selected: set[str]) -> None:\n    previous = manifest_paths(git_bytes(git, \"show\", \"HEAD:\" + MANIFEST_NAME, optional=True))\n    ignored = {name for name in decode_paths(git_bytes(\n        git, \"ls-files\", \"--others\", \"--ignored\", \"--exclude-standard\", \"-z\",\n    )) if eligible(name)}\n    excluded = sorted((previous | ignored) - selected)\n    print(\"Hash basis: raw staged Git blob contents (not working-directory bytes).\")\n    if excluded:\n        print(\"Outside this version-controlled inventory:\")\n        for name in excluded:\n            state = \"present locally\" if (PROJECT_ROOT / name).is_file() else \"absent locally\"\n            print(f\"  {name} [{state}]\")\n        print(\"Retain/recover and explicitly version any research outputs that need archival coverage.\")\n\n\ndef main() -> int:\n    parser = argparse.ArgumentParser(description=__doc__)\n    mode = parser.add_mutually_exclusive_group()\n    mode.add_argument(\"--check\", action=\"store_true\", help=\"Verify the staged manifest against staged inputs.\")\n    mode.add_argument(\"--dry-run\", action=\"store_true\", help=\"Report and hash inputs without writing a manifest.\")\n    args = parser.parse_args()\n    try:\n        for variable in (\"GIT_DIR\", \"GIT_WORK_TREE\", \"GIT_INDEX_FILE\"):\n            if os.environ.get(variable):\n                raise ValueError(f\"Unset {variable} before running this project command.\")\n        git = find_git()\n        root = Path(os.fsdecode(git_bytes(git, \"rev-parse\", \"--show-toplevel\").rstrip(b\"\\r\\n\")))\n        if root.resolve() != PROJECT_ROOT.resolve():\n            raise ValueError(\"Run the script from its own project checkout.\")\n        entries = read_index(git)\n        validate_inputs(git, entries, args.check)\n        hashes = hash_blobs(git, entries)\n        if read_index(git) != entries:\n            raise ValueError(\"The Git index changed during hashing; rerun after staging is complete.\")\n        validate_inputs(git, entries, args.check)\n        data = \"\".join(f\"{digest}  {name}\\n\" for name, digest in hashes.items()).encode(\"utf-8\")\n        report_inventory(git, set(hashes))\n        if args.check:\n            if MANIFEST_NAME not in entries:\n                raise ValueError(\"Stage CHECKSUMS.sha256 before using --check.\")\n            recorded = git_bytes(git, \"cat-file\", \"blob\", entries[MANIFEST_NAME][1])\n            if recorded != data:\n                raise ValueError(\"The staged manifest is stale. Regenerate it, stage it, then rerun --check.\")\n            print(f\"Staged checksum manifest PASSED: {len(hashes)} files.\")\n        elif args.dry_run:\n            print(f\"Dry run: {len(hashes)} staged inputs; no manifest written.\")\n        else:\n            output = PROJECT_ROOT / MANIFEST_NAME\n            # All validation and hashing finish before the existing manifest is replaced.\n            temporary = None\n            try:\n                with tempfile.NamedTemporaryFile(dir=PROJECT_ROOT, prefix=\".checksums-\", delete=False) as stream:\n                    temporary = Path(stream.name)\n                    stream.write(data)\n                temporary.replace(output)\n            finally:\n                if temporary is not None:\n                    temporary.unlink(missing_ok=True)\n            print(f\"Wrote {len(hashes)} SHA-256 checksums to {output}\")\n            print(\"Next: git add CHECKSUMS.sha256, then rerun this command with --check.\")\n        return 0\n    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError) as error:\n        print(f\"Checksum generation failed: {error}\", file=sys.stderr)\n        return 1\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n",
  "tests/test_checksum_manifest.py": "\"\"\"Exercise the manifest command in isolated, real Git repositories.\"\"\"\n\nfrom hashlib import sha256\nfrom pathlib import Path\nimport shutil\nimport subprocess\nimport sys\n\nimport tempfile\nimport unittest\n\n\nSOURCE = Path(__file__).resolve().parents[1] / \"scripts\" / \"generate_checksums.py\"\nGIT = shutil.which(\"git\")\n\n\ndef git(root, *args):\n    return subprocess.run(\n        [GIT, \"-C\", str(root), *args], check=True,\n        stdout=subprocess.PIPE, stderr=subprocess.PIPE,\n    ).stdout\n\n\ndef write(root, name, data):\n    target = root / name\n    target.parent.mkdir(parents=True, exist_ok=True)\n    target.write_bytes(data)\n\n\ndef make_repo(tmp_path):\n    root = tmp_path / \"project with spaces\"\n    root.mkdir()\n    git(root, \"init\")\n    git(root, \"config\", \"user.name\", \"Checksum test\")\n    git(root, \"config\", \"user.email\", \"checksum-test@example.invalid\")\n    git(root, \"config\", \"core.autocrlf\", \"false\")\n    git(root, \"config\", \"commit.gpgsign\", \"false\")\n    write(root, \"scripts/generate_checksums.py\", SOURCE.read_bytes())\n    write(root, \"README.md\", b\"First line\\nSecond line\\n\")\n    write(root, \"docs/sources/binary.dat\", b\"\\x00\\xff\\r\\n\\x80\\n\\r\\x01\")\n    write(root, \".gitignore\", b\"data/processed/*.csv\\n\")\n    git(root, \"add\", \".\")\n    git(root, \"commit\", \"-m\", \"Initial inputs\")\n    return root\n\n\ndef run(root, *args, success=True):\n    result = subprocess.run(\n        [sys.executable, \"-B\", str(root / \"scripts/generate_checksums.py\"), *args],\n        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,\n    )\n    message = (result.stdout + result.stderr).decode(\"utf-8\", errors=\"replace\")\n    if success:\n        assert result.returncode == 0, message\n    else:\n        assert result.returncode != 0, message\n    return message\n\n\ndef records(root):\n    return dict(\n        (line.split(\"  \", 1)[1], line.split(\"  \", 1)[0])\n        for line in (root / \"CHECKSUMS.sha256\").read_text(encoding=\"utf-8\").splitlines()\n    )\n\n\ndef save_manifest(root):\n    run(root)\n    git(root, \"add\", \"CHECKSUMS.sha256\")\n\n\ndef exercise_manifest_hashes_staged_text_and_binary_bytes(repo):\n    run(repo)\n    found = records(repo)\n    assert found[\"README.md\"] == sha256(b\"First line\\nSecond line\\n\").hexdigest()\n    assert found[\"docs/sources/binary.dat\"] == sha256(b\"\\x00\\xff\\r\\n\\x80\\n\\r\\x01\").hexdigest()\n    assert \"CHECKSUMS.sha256\" not in found\n    assert list(found) == sorted(found)\n\n\ndef exercise_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(repo, tmp_path):\n    manifests = []\n    for ending in (\"lf\", \"crlf\"):\n        clone = tmp_path / ending\n        subprocess.run([GIT, \"clone\", \"--no-hardlinks\", str(repo), str(clone)], check=True,\n                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)\n        git(clone, \"config\", \"core.autocrlf\", \"true\" if ending == \"crlf\" else \"false\")\n        for raw_name in git(clone, \"ls-files\", \"-z\").split(b\"\\0\"):\n            if raw_name:\n                (clone / raw_name.decode(\"utf-8\")).unlink()\n        git(clone, \"checkout-index\", \"--all\", \"--force\")\n        payload = (clone / \"README.md\").read_bytes()\n        assert (b\"\\r\\n\" in payload) == (ending == \"crlf\")\n        run(clone)\n        manifests.append((clone / \"CHECKSUMS.sha256\").read_bytes())\n    assert manifests[0] == manifests[1]\n\n\ndef exercise_unstaged_edit_is_rejected_without_replacing_manifest(repo):\n    save_manifest(repo)\n    old = (repo / \"CHECKSUMS.sha256\").read_bytes()\n    write(repo, \"README.md\", b\"Unstaged scientific change\\n\")\n    message = run(repo, success=False)\n    assert \"README.md\" in message\n    assert (repo / \"CHECKSUMS.sha256\").read_bytes() == old\n\n\ndef exercise_missing_tracked_input_is_rejected_without_replacing_manifest(repo):\n    save_manifest(repo)\n    old = (repo / \"CHECKSUMS.sha256\").read_bytes()\n    (repo / \"README.md\").unlink()\n    assert \"Missing tracked inputs\" in run(repo, success=False)\n    assert (repo / \"CHECKSUMS.sha256\").read_bytes() == old\n\n\ndef exercise_new_nonignored_input_requires_staging(repo):\n    write(repo, \"docs/new_research.md\", b\"New evidence\\n\")\n    assert \"docs/new_research.md\" in run(repo, success=False)\n    assert not (repo / \"CHECKSUMS.sha256\").exists()\n    git(repo, \"add\", \"docs/new_research.md\")\n    run(repo)\n    assert records(repo)[\"docs/new_research.md\"] == sha256(b\"New evidence\\n\").hexdigest()\n\n\ndef exercise_ignored_local_output_is_reported_and_does_not_change_manifest(repo):\n    run(repo)\n    old = (repo / \"CHECKSUMS.sha256\").read_bytes()\n    write(repo, \"data/processed/local.csv\", b\"x,y\\n1,2\\n\")\n    message = run(repo)\n    assert \"data/processed/local.csv [present locally]\" in message\n    assert (repo / \"CHECKSUMS.sha256\").read_bytes() == old\n\n\ndef exercise_force_staged_research_output_enters_manifest(repo):\n    write(repo, \"data/processed/retained.csv\", b\"x,y\\n1,2\\n\")\n    git(repo, \"add\", \"-f\", \"data/processed/retained.csv\")\n    run(repo)\n    assert records(repo)[\"data/processed/retained.csv\"] == sha256(b\"x,y\\n1,2\\n\").hexdigest()\n\n\ndef exercise_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(repo):\n    save_manifest(repo)\n    write(repo, \"README.md\", b\"Reviewed staged change\\n\")\n    git(repo, \"add\", \"README.md\")\n    assert \"stale\" in run(repo, \"--check\", success=False)\n    save_manifest(repo)\n    assert \"PASSED\" in run(repo, \"--check\")\n    assert records(repo)[\"README.md\"] == sha256(b\"Reviewed staged change\\n\").hexdigest()\n\n\ndef exercise_check_requires_staging_the_generated_manifest(repo):\n    run(repo)\n    assert \"Stage CHECKSUMS.sha256\" in run(repo, \"--check\", success=False)\n    git(repo, \"add\", \"CHECKSUMS.sha256\")\n    assert \"PASSED\" in run(repo, \"--check\")\n\n\ndef exercise_check_rejects_unstaged_manifest_edit(repo):\n    save_manifest(repo)\n    write(repo, \"CHECKSUMS.sha256\", b\"Do not overwrite this edit\\n\")\n    message = run(repo, \"--check\", success=False)\n    assert \"CHECKSUMS.sha256\" in message and \"Stage the intended\" in message\n\n\ndef exercise_dry_run_preserves_manifest_and_reports_absent_legacy_entry(repo):\n    save_manifest(repo)\n    old = (repo / \"CHECKSUMS.sha256\").read_bytes()\n    write(repo, \"CHECKSUMS.sha256\", old + b\"0\" * 64 + b\"  data/processed/legacy.csv\\n\")\n    git(repo, \"add\", \"CHECKSUMS.sha256\")\n    git(repo, \"commit\", \"-m\", \"Legacy manifest fixture\")\n    before = (repo / \"CHECKSUMS.sha256\").read_bytes()\n    message = run(repo, \"--dry-run\")\n    assert \"legacy.csv [absent locally]\" in message\n    assert (repo / \"CHECKSUMS.sha256\").read_bytes() == before\n\n\ndef exercise_selected_nonregular_index_entry_is_rejected(repo, mode):\n    oid = git(repo, \"rev-parse\", \"HEAD:README.md\").decode().strip()\n    if mode == \"160000\":\n        oid = git(repo, \"rev-parse\", \"HEAD\").decode().strip()\n    git(repo, \"update-index\", \"--add\", \"--cacheinfo\", f\"{mode},{oid},docs/link.md\")\n    assert \"Expected a regular tracked file\" in run(repo, success=False)\n\n\ndef exercise_lfs_pointer_is_not_misrepresented_as_artifact_bytes(repo):\n    write(repo, \"docs/sources/large.dat\", b\"version https://git-lfs.github.com/spec/v1\\n\"\n          b\"oid sha256:\" + b\"0\" * 64 + b\"\\nsize 123456\\n\")\n    git(repo, \"add\", \"docs/sources/large.dat\")\n    assert \"LFS pointers\" in run(repo, success=False)\n    assert not (repo / \"CHECKSUMS.sha256\").exists()\n\n\ndef exercise_unmerged_selected_input_is_rejected(repo):\n    oid = git(repo, \"rev-parse\", \"HEAD:README.md\").decode().strip()\n    git(repo, \"update-index\", \"--force-remove\", \"README.md\")\n    subprocess.run(\n        [GIT, \"-C\", str(repo), \"update-index\", \"--index-info\"],\n        input=f\"100644 {oid} 1\\tREADME.md\\n100644 {oid} 2\\tREADME.md\\n\".encode(),\n        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,\n    )\n    assert \"Resolve the merge conflict\" in run(repo, success=False)\n\n\ndef exercise_coverage_patterns_include_recursive_sources_and_exclude_figures(repo):\n    for name in (\"src/top.py\", \"src/one/two/deep.py\", \"src/__pycache__/ignored.py\",\n                 \"outputs/figures/example.png\"):\n        write(repo, name, b\"coverage fixture\\n\")\n    git(repo, \"add\", \"src\", \"outputs\")\n    run(repo)\n    found = records(repo)\n    assert \"src/top.py\" in found and \"src/one/two/deep.py\" in found\n    assert \"src/__pycache__/ignored.py\" not in found\n    assert \"outputs/figures/example.png\" not in found\n\n\n@unittest.skipUnless(GIT, \"These integration checks require Git on PATH.\")\nclass TestChecksumManifest(unittest.TestCase):\n    def setUp(self):\n        folder = tempfile.TemporaryDirectory()\n        self.addCleanup(folder.cleanup)\n        self.sandbox = Path(folder.name)\n        self.repo = make_repo(self.sandbox)\n\n    def test_manifest_hashes_staged_text_and_binary_bytes(self):\n        exercise_manifest_hashes_staged_text_and_binary_bytes(self.repo)\n\n    def test_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(self):\n        exercise_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(self.repo, self.sandbox)\n\n    def test_unstaged_edit_is_rejected_without_replacing_manifest(self):\n        exercise_unstaged_edit_is_rejected_without_replacing_manifest(self.repo)\n\n    def test_missing_tracked_input_is_rejected_without_replacing_manifest(self):\n        exercise_missing_tracked_input_is_rejected_without_replacing_manifest(self.repo)\n\n    def test_new_nonignored_input_requires_staging(self):\n        exercise_new_nonignored_input_requires_staging(self.repo)\n\n    def test_ignored_local_output_is_reported_and_does_not_change_manifest(self):\n        exercise_ignored_local_output_is_reported_and_does_not_change_manifest(self.repo)\n\n    def test_force_staged_research_output_enters_manifest(self):\n        exercise_force_staged_research_output_enters_manifest(self.repo)\n\n    def test_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(self):\n        exercise_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(self.repo)\n\n    def test_check_requires_staging_the_generated_manifest(self):\n        exercise_check_requires_staging_the_generated_manifest(self.repo)\n\n    def test_check_rejects_unstaged_manifest_edit(self):\n        exercise_check_rejects_unstaged_manifest_edit(self.repo)\n\n    def test_dry_run_preserves_manifest_and_reports_absent_legacy_entry(self):\n        exercise_dry_run_preserves_manifest_and_reports_absent_legacy_entry(self.repo)\n\n    def test_selected_symlink_index_entry_is_rejected(self):\n        exercise_selected_nonregular_index_entry_is_rejected(self.repo, '120000')\n\n    def test_selected_submodule_index_entry_is_rejected(self):\n        exercise_selected_nonregular_index_entry_is_rejected(self.repo, '160000')\n\n    def test_lfs_pointer_is_not_misrepresented_as_artifact_bytes(self):\n        exercise_lfs_pointer_is_not_misrepresented_as_artifact_bytes(self.repo)\n\n    def test_unmerged_selected_input_is_rejected(self):\n        exercise_unmerged_selected_input_is_rejected(self.repo)\n\n    def test_coverage_patterns_include_recursive_sources_and_exclude_figures(self):\n        exercise_coverage_patterns_include_recursive_sources_and_exclude_figures(self.repo)\n\n\nif __name__ == \"__main__\":\n    unittest.main()\n",
  "docs/CHECKSUM_MANIFEST.md": "# Checksum manifest policy\n\n`CHECKSUMS.sha256` records the SHA-256 of the contents staged in Git for the selected reproducibility-critical files. SHA-256 is calculated on the file's stored blob bytes, without Git's object header. The manifest does not hash itself.\n\nThis policy replaces hashing arbitrary files found in a local working directory. The earlier method could include ignored research outputs available on only one computer and could produce different hashes after Git converted LF and CRLF line endings.\n\n## Coverage\n\nThe inventory consists of staged, regular files matching the root-file list and patterns in `scripts/generate_checksums.py`. Those patterns cover the selected source code, tests, notebooks, documentation, processed CSV/JSON artifacts, workflows, packaging files, and source materials when they are version controlled. `.gitattributes` is included if present and tracked.\n\nIgnored local artifacts are excluded and reported. Nonignored new files matching the inventory must be reviewed and staged before generation. Missing tracked inputs and unstaged edits to selected inputs cause failure before the manifest is replaced.\n\nThe current patterns do not cover every repository file. For example, generated figure PNG files are outside these patterns. A manifest check therefore certifies this inventory, not all files, the scientific accuracy of the models, or independently reproduced research results.\n\n## Normal workflow\n\nRun the scientific and software checks appropriate to the change. Review `git status --short`, then stage the intended input files using explicit paths:\n\n```text\ngit add PATH_TO_CHANGED_INPUT PATH_TO_ANOTHER_CHANGED_INPUT\npython scripts/generate_checksums.py\ngit add CHECKSUMS.sha256\npython scripts/generate_checksums.py --check\ngit diff --cached --check\n```\n\nThe first line is a template: replace its example paths with the actual files being committed. Review the staged diff before committing.\n\n`--check` verifies the staged manifest against staged inputs and also rejects unstaged edits to the selected inputs or manifest. It does not regenerate the manifest to make a failure disappear. After changing an input again, stage that change and repeat generation and checking.\n\nUse `python scripts/generate_checksums.py --dry-run` after staging to inspect the inventory without writing the manifest. The command requires a Git checkout and Git itself; it also looks for standard Git for Windows and GitHub Desktop installations if Git is absent from PATH.\n\n## Line endings and binary files\n\nGit may present a tracked text file with different line endings on different machines. Hashing the same staged blob yields the same digest regardless of that presentation. Stored CRLF bytes are retained if they are actually part of the Git blob; the script does not universally rewrite text to LF.\n\nBinary files are hashed from their complete stored bytes. The script does not perform decoding, newline substitution, or text-mode reads on their payloads. LFS pointer files are rejected because the referenced external data needs a separate checksum policy. Selected symbolic links, submodules, and unresolved merge entries are also rejected.\n\nThe manifest is primarily a Git snapshot record. A Git source archive supplies stored blob contents, but any archive export transformations need separate review. A Windows working-directory copy cannot necessarily be checked by an ordinary raw-file checksum utility because Git may have converted its line endings. Use the project's `--check` command inside the checkout. Standalone archive-verification tooling is outside this change.\n\n## Migration from the v1.0.0 manifest\n\nThe published v1.0.0 record remains immutable. Regenerating the manifest under this policy can change hashes and remove entries which were never version controlled. The command reports those exclusions by comparing the inventory with the manifest in `HEAD` and by listing eligible ignored local files.\n\nThe initial cross-computer review identified these four entries from the earlier manifest which were absent from the second computer's regenerated inventory:\n\n- `data/processed/burden_decision_readiness_step_24_20.csv`\n- `data/processed/burden_evidence_tiers_step_24_17.csv`\n- `data/processed/burden_screening_scenarios_step_24_17.csv`\n- `data/processed/burden_structural_uncertainty_step_24_18.csv`\n\nGit reported no tracked `data/processed/burden_*.csv` files on that branch. Those artifacts must be recovered from retained originals or reproduced from their generating code and reviewed before being added to the archival inventory. Exclusion from the new manifest neither recovers them nor establishes that they are scientifically unnecessary. The generator does not delete local artifacts or change `.gitignore` rules.\n\nThe project should separately decide which historical research outputs to retain under version control. A checksum entry alone does not publish or back up a file.\n\n## Implementation references\n\n- [Git index inventory and stage records](https://git-scm.com/docs/git-ls-files)\n- [Reading stored Git object contents](https://git-scm.com/docs/git-cat-file)\n- [Git text conversion and attributes](https://git-scm.com/docs/gitattributes)\n"
}

README_BLOCK = """<!-- BEGIN STAGED CHECKSUM POLICY -->
The manifest records selected **staged Git contents**. Stage the intended input
files before generating it. Then stage `CHECKSUMS.sha256` and run
`python scripts/generate_checksums.py --check` before committing.
The [checksum policy](docs/CHECKSUM_MANIFEST.md) explains inventory coverage,
line endings, binary files, and historical outputs requiring recovery.
<!-- END STAGED CHECKSUM POLICY -->
"""
ADDED = "- Burden-equation provenance document mapping the seven implementations to thesis locations and recording unresolved original-source checks."
FIXED = "- Checksum generation now hashes selected staged Git blob contents, rejects unstaged inputs, and reports local research outputs outside the version-controlled inventory."


def decode(data):
    return data.decode("utf-8-sig").replace("\r\n", "\n")


def encode(text, original=b""):
    ending = "\r\n" if b"\r\n" in original else "\n"
    body = text.replace("\r\n", "\n").replace("\n", ending).encode("utf-8")
    return (b"\xef\xbb\xbf" if original.startswith(b"\xef\xbb\xbf") else b"") + body


def update_readme(text):
    begin = "<!-- BEGIN STAGED CHECKSUM POLICY -->"
    end = "<!-- END STAGED CHECKSUM POLICY -->"
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1:
            raise ValueError("Inspect duplicate or incomplete README checksum markers.")
        found = text[text.index(begin):text.index(end) + len(end)]
        if found != README_BLOCK.rstrip("\n"):
            raise ValueError("The existing README checksum policy differs; inspect before replacing it.")
        return text
    heading = "## Regenerate the integrity manifest"
    if text.count(heading) != 1:
        raise ValueError("Expected one README integrity-manifest heading.")
    return text.replace(heading, heading + "\n\n" + README_BLOCK.rstrip("\n"), 1)


def update_changelog(text, has_provenance):
    marker = "## [Unreleased]"
    if text.count(marker) != 1:
        raise ValueError("Expected one Unreleased changelog heading.")
    start = text.index(marker) + len(marker)
    next_section = re.search(r"^## ", text[start:], re.M)
    end = start + next_section.start() if next_section else len(text)
    body = text[start:end]
    additions = [("Fixed", FIXED)]
    if has_provenance:
        additions.insert(0, ("Added", ADDED))
    for title, entry in additions:
        if entry in body:
            continue
        heading = "### " + title
        match = re.search(r"^" + re.escape(heading) + r"[ \t]*$", body, re.M)
        if match:
            insertion = match.end()
            body = body[:insertion] + "\n\n" + entry + "\n\n" + body[insertion:].lstrip("\n")
        else:
            body = body.rstrip() + "\n\n" + heading + "\n\n" + entry + "\n"
    return text[:start] + body.rstrip() + "\n\n" + text[end:]



def update_workflow(text):
    verification = "run: python scripts/generate_checksums.py --check"
    if text.count(verification) == 1:
        return text
    if verification in text:
        raise ValueError("The workflow has duplicate manifest checks.")
    lines = text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.strip() == "run: python scripts/check_wheel_installation.py"]
    if len(hits) != 1:
        raise ValueError("Expected one installed-wheel check in the CI workflow.")
    start = hits[0] - 1
    while start >= 0 and not lines[start].lstrip().startswith("- name:"):
        start -= 1
    if start < 0:
        raise ValueError("Cannot locate the installed-wheel workflow step.")
    indent = lines[start][:len(lines[start]) - len(lines[start].lstrip())]
    block = (indent + "- name: Verify the Git snapshot checksum manifest\n" +
             indent + "  " + verification + "\n\n")
    return "".join(lines[:start]) + block + "".join(lines[start:])


def update_test_count(text, count):
    if count < 1:
        raise ValueError("The supplied test count must be positive.")
    replacements = [
        (r"\b218 passing automated tests\b", f"{count} passing automated tests"),
        (r"\b218 passing tests\b", f"{count} passing tests"),
        (r"\b218 tests and 228 subtests\b", f"{count} tests and 228 subtests"),
        (r"\b218 tests and\s+228 subtests\b", f"{count} tests and 228 subtests"),
        (r"\b218 passed\b", f"{count} passed"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".checksum-fix-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-count", type=int, help="Update current README/research-note counts after the real suite passes.")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        for relative in ("pyproject.toml", "README.md", "CHANGELOG.md", ".github/workflows/tests.yml", "scripts/generate_checksums.py"):
            if not (root / relative).is_file():
                raise ValueError("Save this installer in the project's scripts directory. Missing: " + relative)
        if not (root / ".git").exists():
            raise ValueError("This installer expects the project Git checkout.")
        generator = root / "scripts/generate_checksums.py"
        current = decode(generator.read_bytes())
        expected_new = PAYLOADS["scripts/generate_checksums.py"]
        old_signature = ast.dump(ast.parse(ORIGINAL_SOURCE), include_attributes=False)
        signature = ast.dump(ast.parse(current), include_attributes=False)
        old_digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()
        if current != expected_new and signature != old_signature:
            raise ValueError("The generator differs from the reviewed version; no files changed. Source signature: " + old_digest)
        originals = {}
        planned = {}
        for relative, value in PAYLOADS.items():
            path = root / relative
            original = path.read_bytes() if path.exists() else None
            originals[relative] = original
            if relative != "scripts/generate_checksums.py" and original is not None and decode(original) != value:
                raise ValueError("An existing file differs from the new template: " + relative)
            planned[relative] = encode(value, original or b"")
        for relative in ("README.md", "CHANGELOG.md", ".github/workflows/tests.yml"):
            originals[relative] = (root / relative).read_bytes()
        planned["README.md"] = encode(update_readme(decode(originals["README.md"])), originals["README.md"])
        planned["CHANGELOG.md"] = encode(update_changelog(
            decode(originals["CHANGELOG.md"]), (root / "docs/BURDEN_MODEL_PROVENANCE.md").is_file()
        ), originals["CHANGELOG.md"])
        planned[".github/workflows/tests.yml"] = encode(update_workflow(
            decode(originals[".github/workflows/tests.yml"])
        ), originals[".github/workflows/tests.yml"])
        if args.test_count is not None:
            for relative in ("README.md", "docs/burden_model_research_note.md"):
                if relative not in originals:
                    originals[relative] = (root / relative).read_bytes()
                base = decode(planned.get(relative, originals[relative]))
                planned[relative] = encode(update_test_count(base, args.test_count), originals[relative])
        for relative, data in planned.items():
            if relative.endswith(".py"):
                ast.parse(data.decode("utf-8-sig"), filename=relative)
        changes = {name: data for name, data in planned.items() if data != originals[name]}
        for name in changes:
            print(("Would update: " if args.dry_run else "Planned: ") + name)
        if args.dry_run:
            print("Dry run finished; no project files changed.")
            return 0
        if not changes:
            print("Checksum fix is already installed; no files changed.")
            return 0
        backup = Path(tempfile.mkdtemp(prefix="blastdesign_checksum_backup_"))
        for name in changes:
            original = originals[name]
            if original is not None:
                target = backup / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(original)
        (backup / "new-files.json").write_text(json.dumps([name for name in changes if originals[name] is None]), encoding="utf-8")
        print("Original-file backups: " + str(backup))
        written = []
        try:
            for name, data in changes.items():
                atomic_write(root / name, data)
                written.append(name)
        except BaseException:
            for name in reversed(written):
                if originals[name] is None:
                    (root / name).unlink(missing_ok=True)
                else:
                    atomic_write(root / name, originals[name])
            raise
        for name in changes:
            print("Updated: " + name)
        print("Installed 16 checksum integration tests. Run the tests before staging.")
        print("Stage intended inputs before generation; stage the generated manifest before --check.")
        print("Versions, release dates, model equations, API baseline, and research data are unchanged.")
        return 0
    except (OSError, UnicodeError, ValueError, SyntaxError) as error:
        print("Checksum fix failed: " + str(error))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
