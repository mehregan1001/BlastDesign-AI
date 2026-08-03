# BlastDesign-AI — portable Step 24.11 checkpoint

This is a reconstructed, self-contained continuation package for Alireza
Mehregan's BlastDesign-AI learning and research project. It is intentionally
complete **through Step 24.11 only**. Step 24.12 has not been performed in the
checkpoint notebook, so it can be repeated as the next learning step.

## Start on a Windows computer

1. Extract the ZIP to a stable location, preferably:

   `F:\Projects\BlastDesign-AI`

2. Open **Anaconda Prompt** in the extracted project folder.
3. Create the environment once:

   ```bat
   conda env create -f environment.yml
   ```

   If the `mining-ai` environment already exists, update it instead:

   ```bat
   conda env update -n mining-ai -f environment.yml --prune
   ```

4. Install the local package in editable mode:

   ```bat
   conda activate mining-ai
   pip install -e .
   ```

5. Start JupyterLab by double-clicking `start_jupyterlab.bat`, or run:

   ```bat
   jupyter lab
   ```

6. Open `notebooks/02_blastdesign_model_audit.ipynb`.
7. Select **Kernel → Restart Kernel and Run All Cells**.
8. Confirm the final green checkpoint message says **Step 24.11 complete**.
9. Resume with Step 24.12 in a new cell, following the next instruction in the
   ChatGPT project conversation.

## Project contents

- `notebooks/01_python_for_blast_engineering.ipynb` — reconstructed first
  learning notebook and blast-pattern calculations.
- `notebooks/02_blastdesign_model_audit.ipynb` — complete model registry and
  seven conventional burden audits through Step 24.11.
- `src/blastdesign/` — reusable, tested Python functions.
- `tests/` — regression tests for benchmark values and piecewise branches.
- `docs/sources/` — available thesis, APCOM paper, Persian conference paper and
  presentation.
- `docs/` — scientific audit, project history and two-computer workflow notes.
- `project_checkpoint.json` — machine-readable checkpoint record.

## Verify the project

From Anaconda Prompt in the project root:

```bat
conda activate mining-ai
pytest -q
```

All tests must pass before continuing research work.

## Important scientific policy

- `legacy` mode will preserve audited BlastDesign equations and behavior for
  historical reproducibility.
- Formula disagreement is not statistical confidence.
- Synthetic outputs from empirical equations will not be presented as field
  data and will not be used to train an ML model as if they were measurements.
- `modern` mode will use applicability screening, uncertainty, operational
  constraints, multi-objective optimization and later field calibration.

## Reconstruction scope

The package reconstructs the work from the retained conversation, validated
equations and available source documents. It is not a byte-for-byte copy of the
files on the home computer. When home access returns, compare the two copies and
retain whichever notebook contains unique personal notes or outputs.
