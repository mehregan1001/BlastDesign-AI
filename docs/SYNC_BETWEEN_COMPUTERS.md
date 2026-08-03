# Working safely on two computers

## Recommended method: private Git repository

A private Git repository gives history, conflict detection and recovery. After
extracting the project on the temporary computer:

```bat
git init
git add .
git commit -m "Portable Step 24.11 checkpoint"
```

Create a private remote repository when convenient, then connect and push it.
On each computer:

1. pull before starting work;
2. edit and run notebooks;
3. save and commit meaningful checkpoints;
4. push before moving to the other computer.

Do not edit the same notebook independently on both computers between pulls.
Jupyter notebooks are JSON files and can be awkward to merge.

## Simpler temporary method

If Git is not yet available, keep one authoritative ZIP or cloud folder and
use dated copies such as:

`02_blastdesign_model_audit_2026-07-31.ipynb`

Before switching computers, copy the newest notebook and `src/` directory.
Never overwrite a newer copy with an older one.

## Files that should remain synchronized

- `notebooks/`
- `src/`
- `tests/`
- `docs/`
- `project_checkpoint.json`
- environment and dependency files

Large immutable source documents under `docs/sources/` need to be copied only
once unless a new version is added.
