# Verification report

## Performed

- Inventoried all 14 files in the source folder and recorded SHA-256 hashes.
- Read and visually inspected all seven pages of the final report.
- Reviewed all five Python source files line by line.
- Parsed all five CSV inputs and confirmed 961 rows, four scenarios and zero
  missing values in each file.
- Recalculated scenario load and available-PV energy from the input datasets;
  the values match the report after rounding to two decimals.
- Performed static Python syntax compilation on all repository source files.
- Ran the repository's static `unittest` checks.
- Checked internal Markdown links and repository scope.
- Compared copied CSV hashes with their originals.

## Not executed

The rule-based and optimization simulations were not executed. Accordingly,
this repository does not claim to reproduce generator energy, final SOC,
temperature trajectories, constraint-check messages or report figures.

## Environment limitations

The audit runtime provided Python 3.12.14 with NumPy and pandas. Matplotlib,
Pyomo, Gurobi and GLPK were not available. The original folder contained
Python 3.14 bytecode caches, but no dependency versions or environment file.

## Evidence classification

- **Report-supported:** both controllers reportedly served load and reached
  80% final EV SOC; qualitative optimizer advantages; generator-energy values.
- **Code-confirmed:** controller sequence, equations, objective coefficients,
  constraints, parameters, signs, scenario initialization and output logic.
- **Data-confirmed:** dimensions, ranges, missing-value status, load energy and
  available-PV energy.
- **Interpretation:** the model is one-step rather than day-ahead; the scenario
  result table likely describes the rule-based controller.
- **Unverified:** numerical controller outputs, comparative efficiency,
  generator cycling, PV curtailment and plotted trajectories.

## Original preservation

Repository preparation used a separate destination folder. No source file was
deleted, renamed or edited.
