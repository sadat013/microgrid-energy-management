# Repository structure and path mapping

## Final structure

```text
microgrid-energy-management/
├── data/
│   ├── README.md
│   └── raw/
│       ├── EV.csv
│       ├── Load.csv
│       ├── P_loss.csv
│       ├── PV.csv
│       └── T_set.csv
├── docs/
│   ├── audit.md
│   ├── data-dictionary.md
│   ├── file-inventory.md
│   ├── issues.md
│   ├── portfolio.md
│   ├── repository-structure.md
│   ├── technical-summary.md
│   ├── verification.md
│   └── workflow.md
├── report/README.md
├── results/README.md
├── src/python/
│   ├── README.md
│   ├── optimization_controller.py
│   ├── param.py
│   ├── rule_based_controller.py
│   ├── run.py
│   └── utils.py
├── tests/
│   └── test_repository.py
├── .gitignore
├── CHANGELOG.md
├── CITATION.cff
├── LICENSE
├── README.md
├── requirements.txt
└── THIRD_PARTY_NOTICES.md
```

## Original-to-final mapping

| Original path | Final path | Treatment |
|---|---|---|
| `Final Simulation File/RB.py` | `src/python/rule_based_controller.py` | Renamed, documented, import guarded |
| `Final Simulation File/OP model combined constraints and variables).py` | `src/python/optimization_controller.py` | Renamed, documented, import guarded |
| `Final Simulation File/param.py` | `src/python/param.py` | Documented; values preserved |
| `Final Simulation File/run.py` | `src/python/run.py` | Portable paths and entry metadata |
| `Final Simulation File/utils.py` | `src/python/utils.py` | Non-overwriting result path |
| `Final Simulation File/*.csv` | `data/raw/*.csv` | Byte-for-byte copies |
| `Data and Forecasting in Microgrid Assignment I.pdf` | Not public | Local ignored reference |
| `Final Simulation File/__pycache__/*` | Not copied | Generated cache excluded |
