# Project audit

## Source inventory

The source folder contained 14 files totaling 1,869,324 bytes:

| Class | Count | Role | Publication decision |
|---|---:|---|---|
| Final report PDF | 1 | Technical context and reported results | Private reference only |
| Python source | 5 | Controllers, parameters, simulation and plots | Publish with low-risk packaging edits |
| CSV input data | 5 | Four scenario profiles | Publish with provenance notice |
| Python bytecode cache | 3 | Generated interpreter artifacts | Exclude |

There was no Git repository, README, license, dependency file, notebook,
MATLAB code, configuration file or automated test suite.

## Important source files

| Original file | Role |
|---|---|
| `RB.py` | Reactive controller and Scenario 4 entry point |
| `OP model combined constraints and variables).py` | Pyomo mixed-integer controller and four-scenario entry point |
| `run.py` | Loads inputs, advances energy/temperature states and calls controllers |
| `param.py` | Simulation, PV, generator, battery, EV and heat-pump parameters |
| `utils.py` | Constraint checks, printed energy totals and four-panel figures |
| `Load.csv` | Electrical demand profile |
| `PV.csv` | PV availability profile |
| `EV.csv` | EV connection state |
| `P_loss.csv` | Envelope thermal-loss profile |
| `T_set.csv` | Indoor-temperature setpoint |

## Scope and objective

The project studies supervisory energy management for a small microgrid with
PV, stationary battery storage, a bidirectional EV, a heat pump, a building
load and a dispatchable generator. Its purpose is to compare a transparent
rule hierarchy with a mathematical dispatch model under standard, high-PV,
low-PV and tight-EV-window scenarios.

## Report-code-data relationships

- The report flowchart corresponds to the priority sequence in
  `rule_based_controller.py`.
- The report's decision variables and objective penalties correspond to the
  Pyomo variables and coefficients in `optimization_controller.py`.
- `run.py` selects columns `S1`-`S4` from every CSV and provides each time step
  to either controller.
- `utils.py` produces the four plot panels shown in the report: electrical
  power, battery/EV power, SOC and indoor temperature.
- The report's load and available-PV energy values reproduce from the CSV
  profiles and documented scaling.

## Publication risks

- The PDF contains three student names and multi-institution branding.
- Dataset authorship and redistribution terms are unstated.
- Gurobi has separate proprietary licensing requirements.
- Individual team-member contributions are not documented.
- Report claims about predictive optimization are inconsistent with the
  supplied scalar model.

The original folder was preserved. Publication work was performed in a new
repository directory.
