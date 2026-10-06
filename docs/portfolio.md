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

As part of a three-person team, I contributed to **[confirm Md Atiq Aziz's
specific responsibilities: controller design, Pyomo formulation, Python
implementation, scenario analysis, figures and/or report sections]**.

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

The project shows why a transparent baseline is valuable when evaluating an
optimizer, and why forecast horizon, terminal constraints, state units and
result provenance must be explicit before claiming predictive performance.

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

Developed and documented rule-based and Pyomo mixed-integer energy-management
controllers for a PV-battery-EV-heat-pump microgrid across four 24-hour
scenarios at 1.5-minute resolution.

## LinkedIn project description

Built a Python microgrid energy-management study comparing transparent
rule-based dispatch with constrained mixed-integer control for PV, stationary
storage, an EV with V2H capability, a heat pump and generator backup. The work
covered four daily scenarios and included energy/SOC dynamics, thermal comfort,
device constraints, scenario visualization and a reproducibility-focused
GitHub publication. Team contribution details: **[confirm before publishing]**.
