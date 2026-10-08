# Change log

## 2026-10-08

### Portfolio details completed

- Added Md Atiq Aziz's evidence-bounded team contribution to the README and
  portfolio summary.
- Rewrote the learning statement, CV bullet and LinkedIn description in
  accurate first-person wording.
- Added the academic contact email and GitHub portfolio link; no unsupported
  LinkedIn URL was invented.

## 2026-10-06

### Published

- Public repository: <https://github.com/sadat013/microgrid-energy-management>

### Created

- GitHub-oriented repository structure.
- Professional project README, citation metadata, MIT license and third-party
  notices.
- Technical audit, data dictionary, workflow, issue register, verification
  report and portfolio summary.
- Static repository tests.

### Copied without numerical changes

- Five source CSV datasets to `data/raw/`.
- Five Python files to `src/python/`.

### Renamed

- `Final Simulation File/RB.py` to
  `src/python/rule_based_controller.py`.
- `Final Simulation File/OP model combined constraints and variables).py` to
  `src/python/optimization_controller.py`.

### Edited without changing scientific equations or constants

- Added module and function documentation.
- Replaced working-directory-dependent data paths with repository-relative
  paths.
- Added import-safe `main` guards and command-line scenario selection.
- Changed plot destinations to unique controller/scenario filenames in
  `results/` to prevent overwriting.
- Removed inherited trailing whitespace from `src/python/run.py`.

### Excluded

- Python bytecode caches.
- The branded team report, retained only as a local ignored reference.
