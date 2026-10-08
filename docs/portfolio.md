# Portfolio summary

## Short title

Microgrid Energy Management with Rule-Based and Mixed-Integer Control

## One-line description

Compared deterministic priority dispatch with Pyomo-based mixed-integer control
for a PV, battery, EV, heat-pump and generator microgrid across four daily
operating scenarios.

## Project summary

This DENSYS 2.0 team project examined supervisory energy management for a
residential microgrid combining photovoltaic generation, stationary battery
storage, a bidirectional electric vehicle, a heat pump and a dispatchable
generator. A rule-based controller prioritized thermal comfort, minimum EV
charging, PV self-consumption, storage dispatch, vehicle-to-home support and
generator backup. A Pyomo mixed-integer model represented the same equipment
using power-balance, state-of-charge, operating-mode, temperature and generator
constraints with a weighted operational objective. Four 24-hour scenarios
tested standard operation, high PV availability, low PV availability and a
tight EV connection window. The published repository adds reproducible data
paths, command-line scenario selection, dependency guidance, static checks and
an explicit engineering audit. Input-energy totals were independently verified;
controller outcomes remain report-based because the simulations were not
rerun during publication.

## Engineering challenge

Coordinate electrical and thermal demand with intermittent PV and limited
storage while meeting an EV departure target and respecting device limits.

## My technical contribution

As part of a three-person DENSYS team, I contributed to the engineering analysis,
scenario interpretation, figures and technical documentation for the
rule-based and optimization-based energy-management approaches. I examined how
the dispatch logic and model constraints coordinate PV, stationary storage, an
EV, a heat pump and generator backup across the four operating scenarios. For
the public release, I also organized the source code and datasets, checked the
input-energy totals, and documented the difference between report-supported
results and results reproduced during the repository audit. This was a
collaborative project; I do not claim sole authorship of every controller or
code module.

## Tools and methods

Python, NumPy, pandas, Matplotlib, Pyomo, mixed-integer linear optimization,
rule-based control, energy balances, SOC dynamics, thermal modeling, scenario
analysis and technical documentation.

## Achievements

- Modeled coordinated power dispatch across five interacting microgrid assets.
- Implemented both interpretable priority logic and a constrained Pyomo model.
- Evaluated four 24-hour scenarios at 1.5-minute resolution.
- Verified input load and PV energy totals against the academic report.
- Converted an academic submission into a documented, testable GitHub project.

## Verified metrics

- 961 samples per 24-hour scenario.
- Four scenarios with no missing input values.
- Load energy from 12.68 to 21.14 kWh across the scenarios.
- Available PV energy from 8.69 to 52.15 kWh.

The reported 80% final EV SOC and generator-energy values were not independently
reproduced and should be presented as report results, not verified reruns.

## Skills demonstrated

Energy-system modeling, microgrid control, storage and EV scheduling, thermal
modeling, optimization formulation, Python engineering, data validation,
technical writing, reproducibility and responsible result communication.

## What I learned

I learned why a transparent rule-based controller is a valuable baseline for
evaluating an optimization-based energy-management strategy. The project also
strengthened my understanding of how objective weights, forecast horizon,
terminal state-of-charge constraints, thermal comfort and consistent state
units affect the apparent performance of a microgrid controller. Most
importantly, I learned to trace engineering claims back to executable code,
validated inputs and clearly identified result sources.

## Suggested visuals

- Simplified microgrid architecture diagram.
- Rule-based dispatch flowchart recreated without institutional branding.
- Side-by-side controller plots for one scenario after a verified rerun.
- Compact table separating data-confirmed and simulation-confirmed metrics.

## Suggested GitHub topics

`microgrid`, `energy-management-system`, `pyomo`, `mixed-integer-programming`,
`rule-based-control`, `battery-storage`, `electric-vehicle`, `heat-pump`,
`photovoltaic`, `energy-engineering`

## CV bullet

Contributed to a three-person DENSYS project comparing rule-based and Pyomo
mixed-integer energy-management controllers for a PV-battery-EV-heat-pump
microgrid across four 24-hour scenarios at 1.5-minute resolution.

## LinkedIn project description

As part of a three-person DENSYS team, I contributed to a Python microgrid
energy-management study comparing transparent rule-based dispatch with
constrained mixed-integer control for PV, stationary storage, an EV with V2H
capability, a heat pump and generator backup. My work focused on engineering
analysis, scenario interpretation, figures and technical documentation. I also
prepared the public repository by organizing the code and data, checking input
energy totals, and clearly separating report-supported results from reproduced
checks.
