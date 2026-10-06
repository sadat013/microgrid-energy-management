# Data dictionary

All datasets are semicolon-delimited and contain 961 indexed rows with scenario
columns `S1`, `S2`, `S3` and `S4`. No missing values were detected.

| File | Interpretation | Observed range | Transformation |
|---|---|---|---|
| `Load.csv` | Building electrical demand | 0 to 5,119.93 | divide by 1000 to kW |
| `PV.csv` | Available PV input | 0 to 918 | divide by 100 to kW |
| `EV.csv` | EV connected | 0 or 1 | none |
| `P_loss.csv` | Envelope heat loss | 0 to 1.819 | treated as kW thermal |
| `T_set.csv` | Indoor setpoint | 15 to 20 | degrees Celsius |

## Confirmed input-energy totals

Using `delta_t = 0.025 h` and the transformations in `run.py`:

| Scenario | Electrical load (kWh) | Available PV (kWh) |
|---|---:|---:|
| S1 | 19.0530 | 26.0738 |
| S2 | 15.9391 | 52.1475 |
| S3 | 12.6816 | 8.6913 |
| S4 | 21.1408 | 52.1475 |

The upstream unit represented by the raw PV values is not documented. The
repository therefore records only the implemented scaling rather than
asserting an unverified source unit.
