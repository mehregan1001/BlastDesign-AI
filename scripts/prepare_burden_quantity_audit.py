"""Prepare a concise documentation-only burden-definition audit."""
import argparse
import ast
import codecs
import hashlib
from pathlib import Path
import re
import tempfile

DOC = """# Diameter and burden definition audit

Review date: 31 October 2026.

## Scope

The current evaluator supplies one hole-diameter input to seven reconstructed
equations. All results appear under `burden_m`. These software conventions do
not establish that the original sources use identical diameters, charging
conditions, or burden quantities.

## Evidence ledger

| Model | Diameter evidence | Burden definition and remaining work |
|---|---|---|
| Ash | The MSc thesis identifies hole diameter. The later FHWA handbook, printed p. 352, uses explosive charge diameter. | The original Ash burden convention and coefficient conditions remain to be checked. Record the intended source edition and any coupling assumption. |
| Bhandari–Vutukuri | MSc Eq. 2-6 identifies hole diameter in metres. | The originating source's practical/maximum/nominal burden convention remains unresolved. Inspect the cited book page and original publication. |
| Lopez Jimeno | MSc Tables 2-3 and 2-4 identify hole diameter. | Inspect the original table headings and surrounding text for burden, charging, geometry, adjustment, and branch conditions. |
| Konya 1972 | The MSc thesis and later FHWA handbook identify explosive charge diameter. | The code passes hole diameter and retains exponent 0.33. Verify the originating publication and its burden conditions; the later handbook is not a complete original-source audit. |
| Konya 1983 | The MSc equation shares the preceding charge-diameter context. | This is a thesis-context reading. Verify the original 1983 variable definitions and burden conditions; do not treat the handbook's 1972 definition as independent verification of this version. |
| Rustan | The existing source audit records borehole diameter and the 89–381 mm interval. | Eq. 18 defines normalized practical burden B_p1 = sqrt(B_p * S_p), and Eq. 22 estimates B_p1 for S/B = 1. Retain the documented 18.1/18.8 source discrepancy and establish any mapping to another burden target. |
| Tatiya–Al-Ajmi | The thesis and authors' institutional abstract identify blast-hole diameter. | The full coefficient table and precise burden convention remain unchecked. Record the ANFO condition and reported 25–304 mm study scope. |

## Interpretation

Existing ensemble statistics describe reconstructed formula outputs under the
recorded input convention. Equivalence to one identical operational burden
target has not been established across all seven original sources.
The spread may reflect equation differences and unresolved differences in
definitions or source conditions. Their contributions have not been separated.
The historical A/B/C tiers do not certify physical-quantity equivalence.

For a charge-diameter expression, substituting hole diameter supplies a full
radial-coupling diameter assumption. This does not establish complete
longitudinal loading, explosive performance, or applicability to decoupled charges.
Likewise, Rustan's normalized burden must not silently become a practical burden
for arbitrary spacing. A conversion requires documented definitions and inputs.

## Sources and limits

- MSc thesis: Sections 2-2-3 through 2-2-8, Eqs. 2-4 and 2-6 to 2-12,
  Tables 2-3 to 2-5. Recovered thesis text was inspected; complete visual
  inspection of the Word document is not claimed.
- Konya and Walter (1991), FHWA-HI-92-001, printed p. 352:
  [USDOT record](https://rosap.ntl.bts.gov/view/dot/743).
  Indexed equation text was checked on 31 October 2026; the original Ash,
  1972 Konya, and 1983 Konya publications were not newly visually inspected.
- [Rustan source audit](RUSTAN_SOURCE_AUDIT.md): supplied images of printed
  pp. 146–147, Eqs. 18 and 22, visually checked on 25 October 2026.
- [Tatiya and Al-Ajmi institutional abstract](https://squ.elsevierpure.com/en/publications/evaluation-of-the-atlas-copco-relation-between-burden-and-blast-h/):
  checked on 31 October 2026; the full coefficient table remains unchecked.
- [Model provenance review](BURDEN_MODEL_PROVENANCE.md): other source chains
  and outstanding evidence requests.

No equation, numerical artifact, historical tier, API schema, or release version
is changed by this documentation step. Original-source completion and target
harmonization remain open. The decision gate remains
`RESEARCH_COMPARATOR_ONLY`; this audit supplies no operational recommendation.
"""

START = "<!-- BEGIN BURDEN QUANTITY AUDIT -->"
END = "<!-- END BURDEN QUANTITY AUDIT -->"
README = """### Engineering definitions in the comparison

The seven-model statistics summarize reconstructed legacy formula outputs.
Their diameter definitions, burden targets, and charging/geometry assumptions
have not yet been fully harmonized across the original sources.
The spread may reflect definition and source-condition differences as well as
equation differences; these contributions have not been separated.
See the [definition audit](docs/BURDEN_QUANTITY_AUDIT.md).
The decision gate remains `RESEARCH_COMPARATOR_ONLY`."""
NOTE = """## Engineering definitions and comparability

The evaluator's shared hole-diameter input and `burden_m` column reproduce the
legacy comparison but do not establish identical original-source quantities.
Ensemble statistics are descriptive summaries of reconstructed formula outputs.
The contributions of equation differences and unresolved definition/condition
differences have not been separated. A/B/C tiers do not certify quantity
equivalence. See the [definition audit](BURDEN_QUANTITY_AUDIT.md).
Historical results are retained; `RESEARCH_COMPARATOR_ONLY` still applies."""
OLD_P02 = "| P02 | Diameter can mean charge diameter or hole diameter | Record the source definition for each equation and the coupling assumption used in comparisons |"
NEW_P02 = "| P02 | Diameter and burden definitions require model-specific reconciliation | See [BURDEN_QUANTITY_AUDIT.md](BURDEN_QUANTITY_AUDIT.md); source completion and target harmonization remain open |"


def text(raw):
    return raw.decode("utf-8-sig").replace("\r\n", "\n")


def marked(body):
    return START + "\n" + body + "\n" + END


def add_block(content, body, heading=None):
    block = marked(body)
    if START in content or END in content:
        if content.count(START) != 1 or content.count(END) != 1 or block not in content:
            raise ValueError("An existing audit block differs; preserve and review it.")
        return content
    if heading:
        matches = list(re.finditer("^" + re.escape(heading) + "$", content, re.M))
        if len(matches) != 1:
            raise ValueError("Expected one section: " + heading)
        tail = matches[0].end()
        following = re.search(r"^## ", content[tail:], re.M)
        stop = tail + following.start() if following else len(content)
    else:
        stop = len(content)
    return content[:stop].rstrip("\n") + "\n\n" + block + ("\n\n" if content[stop:] else "\n") + content[stop:]


def snapshot(root):
    paths = [root / name for name in (
        "pyproject.toml", "CITATION.cff", "CHECKSUMS.sha256",
        ".git/index", ".git/HEAD", ".gitignore", ".gitattributes",
    )]
    for pattern in (
        "src/**/*.py", "tests/**/*.py", "data/processed/**/*.csv",
        "data/processed/**/*.json", "notebooks/**/*.ipynb",
        "outputs/figures/**/*.png", "outputs/figures/**/*.svg",
    ):
        paths.extend(root.glob(pattern))
    return {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths if p.is_file()}


def replace(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(data)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if not (root / ".git").exists():
        raise ValueError("Save this script in the project scripts folder.")
    for name in ("docs/RUSTAN_SOURCE_AUDIT.md", "docs/LEGACY_OUTPUT_ARCHIVE.md"):
        if not (root / name).is_file():
            raise ValueError("Fetch/Pull the completed Rustan fix first: " + name)
    module = ast.parse(text((root / "src/blastdesign/burden.py").read_bytes()))
    helpers = [n for n in module.body if isinstance(n, ast.FunctionDef)
               and n.name == "rustan_applicability"]
    if len(helpers) != 1 or not any(
        isinstance(n, ast.Constant) and n.value == 381 for n in ast.walk(helpers[0])
    ):
        raise ValueError("The Rustan 381 mm correction must be present first.")
    protected = snapshot(root)
    plans = {}

    def plan(name, transform):
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Refusing a linked destination: " + name)
        before = path.read_bytes() if path.exists() else None
        original = text(before) if before is not None else None
        after = transform(original)
        if after == original:
            return
        ending = "\r\n" if before and b"\r\n" in before else "\n"
        bom = codecs.BOM_UTF8 if before and before.startswith(codecs.BOM_UTF8) else b""
        plans[name] = (before, bom + after.replace("\n", ending).encode("utf-8"))

    def new_audit(current):
        if current is not None and current != DOC:
            raise ValueError("An existing audit document differs; it was preserved.")
        return DOC

    def provenance(current):
        if current.count(NEW_P02) == 1 and OLD_P02 not in current:
            return current
        if current.count(OLD_P02) != 1 or NEW_P02 in current:
            raise ValueError("The provenance P02 row needs review.")
        return current.replace(OLD_P02, NEW_P02, 1)

    def changelog(current):
        matches = list(re.finditer(r"^## \[Unreleased\]$", current, re.M))
        if len(matches) != 1:
            raise ValueError("Expected one Unreleased section.")
        start = matches[0].start()
        following = re.search(r"^## ", current[matches[0].end():], re.M)
        stop = matches[0].end() + following.start() if following else len(current)
        section = current[start:stop]
        for category, entry in (
            ("Added", "Seven-model diameter and burden definition audit recording evidence and unresolved source definitions."),
            ("Changed", "Clarified the interpretation of legacy ensemble statistics while source quantity harmonization remains incomplete."),
        ):
            bullet = "- " + entry + "\n"
            if bullet in section:
                continue
            marker = "### " + category + "\n"
            if section.count(marker) > 1:
                raise ValueError("Duplicate Unreleased category: " + category)
            if marker in section:
                section = section.replace(marker, marker + "\n" + bullet, 1)
            else:
                section = section.rstrip("\n") + "\n\n" + marker + "\n" + bullet + "\n"
        return current[:start] + section + current[stop:]

    plan("docs/BURDEN_QUANTITY_AUDIT.md", new_audit)
    plan("README.md", lambda s: add_block(s, README, "## Initial research finding"))
    plan("docs/burden_model_research_note.md", lambda s: add_block(s, NOTE))
    plan("docs/BURDEN_MODEL_PROVENANCE.md", provenance)
    plan("CHANGELOG.md", changelog)
    if not plans:
        print("Audit already prepared; no files changed.")
        return
    for name in plans:
        print(("Would update: " if args.dry_run else "Planned: ") + name)
    if args.dry_run:
        print("Dry run complete; no files changed.")
        return
    backup = Path(tempfile.mkdtemp(prefix="blastdesign_quantity_backup_"))
    for name, (before, _) in plans.items():
        if before is not None:
            target = backup / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(before)
    (backup / "new-files.txt").write_text(
        "\n".join(n for n, (old, _) in plans.items() if old is None), encoding="utf-8"
    )
    print("Original-file backups:", backup)
    done = []
    try:
        for name, (before, _) in plans.items():
            path = root / name
            actual = path.read_bytes() if path.exists() else None
            if actual != before:
                raise ValueError("Input changed during preparation: " + name)
        if snapshot(root) != protected:
            raise ValueError("Protected inputs changed during preparation.")
        for name, (before, after) in plans.items():
            path = root / name
            if before is None:
                with path.open("xb") as handle:
                    done.append(name)
                    handle.write(after)
            else:
                replace(path, after)
                done.append(name)
        if snapshot(root) != protected:
            raise ValueError("Protected inputs changed during preparation.")
    except BaseException:
        for name in reversed(done):
            before, _ = plans[name]
            if before is None:
                (root / name).unlink()
            else:
                replace(root / name, before)
        raise
    for name in plans:
        print("Updated:", name)
    print("Documentation updated. Equations, numerical artifacts, versions and test counts are unchanged.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, UnicodeError, SyntaxError) as error:
        raise SystemExit("Preparation stopped: " + str(error))