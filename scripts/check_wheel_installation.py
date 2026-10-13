"""Build and test a normal wheel in a fresh temporary virtual environment.

Run from the project environment:
    python scripts/check_wheel_installation.py

The active environment is not changed. The package is built from a temporary
copy of packaging files and src/. Its dependencies and pytest are installed
in a new venv, then the actual repository tests and saved CLI report are run
against that installed wheel. Package origins are checked after test
collection and at session end. Temporary build and environment files are
removed afterward. Network access to the configured package index is needed.
"""

from __future__ import annotations

import argparse
from email.parser import Parser
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile


IMPORT_CHECK = r'''
from importlib import metadata
import json
from pathlib import Path
import sys
import sysconfig
import blastdesign
import blastdesign_ai

expected_version = sys.argv[1]
site_packages = Path(sysconfig.get_path("purelib")).resolve()
for module in (blastdesign, blastdesign_ai):
    source = Path(module.__file__).resolve()
    if not source.is_relative_to(site_packages):
        raise RuntimeError(f"Import outside the installed environment: {source}")
    exports = module.__all__
    assert len(exports) == len(set(exports)), f"Duplicate exports in {module.__name__}"
    assert all(hasattr(module, name) for name in exports), f"Missing exports in {module.__name__}"
    print(f"Installed import: {module.__name__}: {source}")
assert blastdesign_ai.__version__ == metadata.version("blastdesign-ai") == expected_version
assert metadata.metadata("blastdesign-ai")["License-Expression"] == "MIT"
name = "build_gole_gohar_konya_density_elasticity_table"
assert name in blastdesign.__all__ and callable(getattr(blastdesign, name))
direct_url_text = metadata.distribution("blastdesign-ai").read_text("direct_url.json")
if direct_url_text:
    assert not json.loads(direct_url_text).get("dir_info", {}).get("editable", False)
print("Normal installed-wheel imports, public exports, version, and MIT metadata: PASSED")
'''

TEST_HARNESS = r'''
from pathlib import Path
import sys
import sysconfig
import pytest

site_packages = Path(sysconfig.get_path("purelib")).resolve()

def check_package_origins():
    for name, module in list(sys.modules.items()):
        if name in ("blastdesign", "blastdesign_ai") or name.startswith(("blastdesign.", "blastdesign_ai.")):
            source = getattr(module, "__file__", None)
            if source is not None and not Path(source).resolve().is_relative_to(site_packages):
                raise pytest.UsageError(f"Test imported source checkout instead of wheel: {name}: {source}")

class WheelOriginGuard:
    def pytest_collection_finish(self, session):
        check_package_origins()

    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session, exitstatus):
        check_package_origins()

raise SystemExit(pytest.main(
    ["-c", sys.argv[1], "-o", "pythonpath=",
     "-o", f"cache_dir={Path(__file__).resolve().parent / 'pytest_cache'}",
     "--import-mode=importlib", sys.argv[2], "-q"],
    plugins=[WheelOriginGuard()],
))
'''


def run_command(arguments: list[str], cwd: Path, environment: dict[str, str]) -> None:
    subprocess.run(arguments, cwd=cwd, env=environment, check=True)


def read_wheel_version(wheel: Path) -> str:
    with zipfile.ZipFile(wheel) as archive:
        candidates = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
        if len(candidates) != 1:
            raise ValueError("Expected exactly one distribution metadata file in the wheel.")
        package = Parser().parsestr(archive.read(candidates[0]).decode("utf-8"))
    if package.get("Name", "").lower().replace("_", "-") != "blastdesign-ai":
        raise ValueError("Unexpected distribution name in the built wheel.")
    if package.get("License-Expression") != "MIT":
        raise ValueError("The built wheel does not declare License-Expression: MIT.")
    version = package.get("Version")
    if not version:
        raise ValueError("The built wheel has no version.")
    return version


def check_wheel(root: Path) -> None:
    config = root / "pyproject.toml"
    tests = root / "tests"
    report = root / "data" / "processed" / "burden_decision_report_step_24_21.json"
    for required in (config, root / "README.md", root / "LICENSE", report):
        if not required.is_file():
            raise ValueError(f"Required project file not found: {required}")
    if not tests.is_dir() or not (root / "src" / "blastdesign").is_dir():
        raise ValueError("Expected the project's tests/ and src/blastdesign/ directories.")
    environment = os.environ.copy()
    for name in (
        "PYTHONPATH", "PYTHONHOME", "PYTEST_ADDOPTS", "PYTEST_PLUGINS",
        "PIP_TARGET", "PIP_PREFIX", "PIP_USER",
    ):
        environment.pop(name, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    environment["MPLBACKEND"] = "Agg"
    with tempfile.TemporaryDirectory(prefix="bdwheel_") as directory:
        workspace = Path(directory)
        build_project = workspace / "project"
        build_project.mkdir()
        for relative in (
            "pyproject.toml", "README.md", "LICENSE", "CITATION.cff",
            "MANIFEST.in", "setup.cfg", "setup.py",
        ):
            source = root / relative
            if source.is_file():
                shutil.copy2(source, build_project / relative)
        shutil.copytree(
            root / "src", build_project / "src",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.egg-info"),
        )
        env_directory = workspace / "env"
        print("1. Creating a fresh virtual environment:", env_directory, flush=True)
        venv.EnvBuilder(with_pip=True, system_site_packages=False).create(env_directory)
        python = env_directory / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        wheels = workspace / "wheels"
        wheels.mkdir()
        print("2. Building the normal wheel with build isolation", flush=True)
        run_command([
            str(python), "-I", "-B", "-m", "pip", "wheel", "--no-deps",
            "--wheel-dir", str(wheels), str(build_project),
        ], workspace, environment)
        candidates = list(wheels.glob("*.whl"))
        if len(candidates) != 1:
            raise ValueError(f"Expected one project wheel; found {len(candidates)}.")
        wheel = candidates[0]
        version = read_wheel_version(wheel)
        print("3. Installing the wheel, declared dependencies, and pytest into the fresh environment", flush=True)
        run_command([
            str(python), "-I", "-B", "-m", "pip", "install", str(wheel), "pytest>=9",
        ], workspace, environment)
        run_command([str(python), "-I", "-B", "-m", "pip", "check"], workspace, environment)
        print("4. Verifying installed imports and metadata", flush=True)
        run_command([str(python), "-I", "-B", "-c", IMPORT_CHECK, version], workspace, environment)
        print("5. Running the real project tests against the installed wheel", flush=True)
        harness = workspace / "wheel_test_harness.py"
        harness.write_text(TEST_HARNESS, encoding="utf-8")
        run_command([
            str(python), "-I", "-B", str(harness), str(config), str(tests),
        ], workspace, environment)
        print("6. Checking the installed command-line entry point", flush=True)
        cli = env_directory / (
            "Scripts/blastdesign-validate.exe" if os.name == "nt" else "bin/blastdesign-validate"
        )
        run_command([str(cli), str(report)], workspace, environment)
        print(f"\nInstalled-wheel release check PASSED (version {version}).", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args()
    try:
        check_wheel(arguments.project_root.resolve())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"\nInstalled-wheel release check FAILED: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
