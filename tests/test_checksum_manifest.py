"""Exercise the manifest command in isolated, real Git repositories."""

from hashlib import sha256
from pathlib import Path
import shutil
import subprocess
import sys

import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "generate_checksums.py"
GIT = shutil.which("git")


def git(root, *args):
    return subprocess.run(
        [GIT, "-C", str(root), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def write(root, name, data):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)


def make_repo(tmp_path):
    root = tmp_path / "project with spaces"
    root.mkdir()
    git(root, "init")
    git(root, "config", "user.name", "Checksum test")
    git(root, "config", "user.email", "checksum-test@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "config", "commit.gpgsign", "false")
    write(root, "scripts/generate_checksums.py", SOURCE.read_bytes())
    write(root, "README.md", b"First line\nSecond line\n")
    write(root, "docs/sources/binary.dat", b"\x00\xff\r\n\x80\n\r\x01")
    write(root, ".gitignore", b"data/processed/*.csv\n")
    git(root, "add", ".")
    git(root, "commit", "-m", "Initial inputs")
    return root


def run(root, *args, success=True):
    result = subprocess.run(
        [sys.executable, "-B", str(root / "scripts/generate_checksums.py"), *args],
        cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    message = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    if success:
        assert result.returncode == 0, message
    else:
        assert result.returncode != 0, message
    return message


def records(root):
    return dict(
        (line.split("  ", 1)[1], line.split("  ", 1)[0])
        for line in (root / "CHECKSUMS.sha256").read_text(encoding="utf-8").splitlines()
    )


def save_manifest(root):
    run(root)
    git(root, "add", "CHECKSUMS.sha256")


def exercise_manifest_hashes_staged_text_and_binary_bytes(repo):
    run(repo)
    found = records(repo)
    assert found["README.md"] == sha256(b"First line\nSecond line\n").hexdigest()
    assert found["docs/sources/binary.dat"] == sha256(b"\x00\xff\r\n\x80\n\r\x01").hexdigest()
    assert "CHECKSUMS.sha256" not in found
    assert list(found) == sorted(found)


def exercise_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(repo, tmp_path):
    manifests = []
    for ending in ("lf", "crlf"):
        clone = tmp_path / ending
        subprocess.run([GIT, "clone", "--no-hardlinks", str(repo), str(clone)], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        git(clone, "config", "core.autocrlf", "true" if ending == "crlf" else "false")
        for raw_name in git(clone, "ls-files", "-z").split(b"\0"):
            if raw_name:
                (clone / raw_name.decode("utf-8")).unlink()
        git(clone, "checkout-index", "--all", "--force")
        payload = (clone / "README.md").read_bytes()
        assert (b"\r\n" in payload) == (ending == "crlf")
        run(clone)
        manifests.append((clone / "CHECKSUMS.sha256").read_bytes())
    assert manifests[0] == manifests[1]


def exercise_unstaged_edit_is_rejected_without_replacing_manifest(repo):
    save_manifest(repo)
    old = (repo / "CHECKSUMS.sha256").read_bytes()
    write(repo, "README.md", b"Unstaged scientific change\n")
    message = run(repo, success=False)
    assert "README.md" in message
    assert (repo / "CHECKSUMS.sha256").read_bytes() == old


def exercise_missing_tracked_input_is_rejected_without_replacing_manifest(repo):
    save_manifest(repo)
    old = (repo / "CHECKSUMS.sha256").read_bytes()
    (repo / "README.md").unlink()
    assert "Missing tracked inputs" in run(repo, success=False)
    assert (repo / "CHECKSUMS.sha256").read_bytes() == old


def exercise_new_nonignored_input_requires_staging(repo):
    write(repo, "docs/new_research.md", b"New evidence\n")
    assert "docs/new_research.md" in run(repo, success=False)
    assert not (repo / "CHECKSUMS.sha256").exists()
    git(repo, "add", "docs/new_research.md")
    run(repo)
    assert records(repo)["docs/new_research.md"] == sha256(b"New evidence\n").hexdigest()


def exercise_ignored_local_output_is_reported_and_does_not_change_manifest(repo):
    run(repo)
    old = (repo / "CHECKSUMS.sha256").read_bytes()
    write(repo, "data/processed/local.csv", b"x,y\n1,2\n")
    message = run(repo)
    assert "data/processed/local.csv [present locally]" in message
    assert (repo / "CHECKSUMS.sha256").read_bytes() == old


def exercise_force_staged_research_output_enters_manifest(repo):
    write(repo, "data/processed/retained.csv", b"x,y\n1,2\n")
    git(repo, "add", "-f", "data/processed/retained.csv")
    run(repo)
    assert records(repo)["data/processed/retained.csv"] == sha256(b"x,y\n1,2\n").hexdigest()


def exercise_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(repo):
    save_manifest(repo)
    write(repo, "README.md", b"Reviewed staged change\n")
    git(repo, "add", "README.md")
    assert "stale" in run(repo, "--check", success=False)
    save_manifest(repo)
    assert "PASSED" in run(repo, "--check")
    assert records(repo)["README.md"] == sha256(b"Reviewed staged change\n").hexdigest()


def exercise_check_requires_staging_the_generated_manifest(repo):
    run(repo)
    assert "Stage CHECKSUMS.sha256" in run(repo, "--check", success=False)
    git(repo, "add", "CHECKSUMS.sha256")
    assert "PASSED" in run(repo, "--check")


def exercise_check_rejects_unstaged_manifest_edit(repo):
    save_manifest(repo)
    write(repo, "CHECKSUMS.sha256", b"Do not overwrite this edit\n")
    message = run(repo, "--check", success=False)
    assert "CHECKSUMS.sha256" in message and "Stage the intended" in message


def exercise_dry_run_preserves_manifest_and_reports_absent_legacy_entry(repo):
    save_manifest(repo)
    old = (repo / "CHECKSUMS.sha256").read_bytes()
    write(repo, "CHECKSUMS.sha256", old + b"0" * 64 + b"  data/processed/legacy.csv\n")
    git(repo, "add", "CHECKSUMS.sha256")
    git(repo, "commit", "-m", "Legacy manifest fixture")
    before = (repo / "CHECKSUMS.sha256").read_bytes()
    message = run(repo, "--dry-run")
    assert "legacy.csv [absent locally]" in message
    assert (repo / "CHECKSUMS.sha256").read_bytes() == before


def exercise_selected_nonregular_index_entry_is_rejected(repo, mode):
    oid = git(repo, "rev-parse", "HEAD:README.md").decode().strip()
    if mode == "160000":
        oid = git(repo, "rev-parse", "HEAD").decode().strip()
    git(repo, "update-index", "--add", "--cacheinfo", f"{mode},{oid},docs/link.md")
    assert "Expected a regular tracked file" in run(repo, success=False)


def exercise_lfs_pointer_is_not_misrepresented_as_artifact_bytes(repo):
    write(repo, "docs/sources/large.dat", b"version https://git-lfs.github.com/spec/v1\n"
          b"oid sha256:" + b"0" * 64 + b"\nsize 123456\n")
    git(repo, "add", "docs/sources/large.dat")
    assert "LFS pointers" in run(repo, success=False)
    assert not (repo / "CHECKSUMS.sha256").exists()


def exercise_unmerged_selected_input_is_rejected(repo):
    oid = git(repo, "rev-parse", "HEAD:README.md").decode().strip()
    git(repo, "update-index", "--force-remove", "README.md")
    subprocess.run(
        [GIT, "-C", str(repo), "update-index", "--index-info"],
        input=f"100644 {oid} 1\tREADME.md\n100644 {oid} 2\tREADME.md\n".encode(),
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    assert "Resolve the merge conflict" in run(repo, success=False)


def exercise_coverage_patterns_include_recursive_sources_and_exclude_figures(repo):
    for name in ("src/top.py", "src/one/two/deep.py", "src/__pycache__/ignored.py",
                 "outputs/figures/example.png"):
        write(repo, name, b"coverage fixture\n")
    git(repo, "add", "src", "outputs")
    run(repo)
    found = records(repo)
    assert "src/top.py" in found and "src/one/two/deep.py" in found
    assert "src/__pycache__/ignored.py" not in found
    assert "outputs/figures/example.png" not in found


@unittest.skipUnless(GIT, "These integration checks require Git on PATH.")
class TestChecksumManifest(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.sandbox = Path(folder.name)
        self.repo = make_repo(self.sandbox)

    def test_manifest_hashes_staged_text_and_binary_bytes(self):
        exercise_manifest_hashes_staged_text_and_binary_bytes(self.repo)

    def test_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(self):
        exercise_same_git_snapshot_has_identical_manifest_in_lf_and_crlf_checkouts(self.repo, self.sandbox)

    def test_unstaged_edit_is_rejected_without_replacing_manifest(self):
        exercise_unstaged_edit_is_rejected_without_replacing_manifest(self.repo)

    def test_missing_tracked_input_is_rejected_without_replacing_manifest(self):
        exercise_missing_tracked_input_is_rejected_without_replacing_manifest(self.repo)

    def test_new_nonignored_input_requires_staging(self):
        exercise_new_nonignored_input_requires_staging(self.repo)

    def test_ignored_local_output_is_reported_and_does_not_change_manifest(self):
        exercise_ignored_local_output_is_reported_and_does_not_change_manifest(self.repo)

    def test_force_staged_research_output_enters_manifest(self):
        exercise_force_staged_research_output_enters_manifest(self.repo)

    def test_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(self):
        exercise_staged_edit_uses_new_index_contents_and_check_rejects_stale_manifest(self.repo)

    def test_check_requires_staging_the_generated_manifest(self):
        exercise_check_requires_staging_the_generated_manifest(self.repo)

    def test_check_rejects_unstaged_manifest_edit(self):
        exercise_check_rejects_unstaged_manifest_edit(self.repo)

    def test_dry_run_preserves_manifest_and_reports_absent_legacy_entry(self):
        exercise_dry_run_preserves_manifest_and_reports_absent_legacy_entry(self.repo)

    def test_selected_symlink_index_entry_is_rejected(self):
        exercise_selected_nonregular_index_entry_is_rejected(self.repo, '120000')

    def test_selected_submodule_index_entry_is_rejected(self):
        exercise_selected_nonregular_index_entry_is_rejected(self.repo, '160000')

    def test_lfs_pointer_is_not_misrepresented_as_artifact_bytes(self):
        exercise_lfs_pointer_is_not_misrepresented_as_artifact_bytes(self.repo)

    def test_unmerged_selected_input_is_rejected(self):
        exercise_unmerged_selected_input_is_rejected(self.repo)

    def test_coverage_patterns_include_recursive_sources_and_exclude_figures(self):
        exercise_coverage_patterns_include_recursive_sources_and_exclude_figures(self.repo)


if __name__ == "__main__":
    unittest.main()
