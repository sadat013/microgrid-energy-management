# Known issues, risks and missing information

## High-impact technical discrepancies

1. **Forecast-horizon mismatch.** The report calls the optimization predictive
   and full-day. The code contains only scalar decision variables and solves
   one interval at a time. It cannot schedule against future PV or load
   profiles as a day-ahead optimizer would.
2. **Electrical power-balance mismatch.** The report adds `P_loss` to
   electrical demand. The code uses `P_loss` as thermal envelope loss in the
   building-temperature equation and omits it from electrical balance. Adding
   a thermal heat-loss term directly to electrical balance would be
   dimensionally inappropriate unless a conversion or different definition is
   supplied.
3. **Reported comparison is not numerically complete.** The scenario table has
   one generator-energy column without identifying the controller. The report
   makes comparative claims but supplies no complete paired metric table.

## Code risks

- `solve_model` checks solver status but not termination condition. Infeasible
  or otherwise unusable solutions can fall through to a zero-command fallback.
- The zero-command fallback violates demand whenever load is nonzero; later
  checks report the imbalance but do not stop the run.
- `T_hp[0]` is initialized to 0 degrees C rather than to the first setpoint or
  a documented initial indoor temperature.
- `np.linspace(0, time_steps * delta_t, time_steps)` produces a plotted endpoint
  of 24.025 h. `np.arange(time_steps) * delta_t` would end at 24 h.
- The optimizer's 30% battery threshold differs from the rule-based 35%
  threshold.
- The report describes ramp limits, but the optimizer only penalizes absolute
  generator and EV charging changes; it does not impose explicit maximum ramp
  constraints.
- EV smoothing considers charging power only, not discharge power.
- `hp_allowed` and `P_pv_max` mutable parameters are set but not used directly
  in active constraints.
- The one-step temperature constraint limits upward temperature change by
  `delta_T_max = 20 K`; it is not the +/-2 degrees C comfort band shown in the
  figures.

## Ambiguous assumptions

- Raw PV units before division by 100 are not documented.
- `SOC_*` arrays store energy in kWh, while controller interfaces use SOC
  fractions. The mixed terminology invites unit mistakes.
- The generator is rounded to integer-kW output only in the rule-based logic;
  the optimizer permits continuous power between its on-state limits.
- Initial indoor temperature, forecast accuracy, grid connection status and
  whether generator fuel use is linear in electrical output are unstated.
- No terminal stationary-battery SOC target is enforced.
- No measured-data or external-model validation is documented.

## Report-quality issues

- Scenario 3 and Scenario 4 cite the wrong figure numbers in the discussion.
- Tables are numbered 2 and 3 even though no Table 1 appears.
- "Tabel" is misspelled in one caption.
- Sources and literature citations are absent.

## Changes requiring engineering approval

The following were intentionally not implemented because they could change
results: replacing the one-step optimizer with a horizon model, changing
temperature initialization, correcting the time vector, adding termination
handling, reconciling heat-loss balance, imposing ramp limits, changing SOC
thresholds, or adding terminal constraints.
