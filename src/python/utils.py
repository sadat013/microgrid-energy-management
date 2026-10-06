"""Constraint checks, summary output and plotting utilities."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from param import (time_steps, delta_t,
                   SOC_min_bss, SOC_max_bss, C_bss, P_nom_bss,
                   SOC_min_ev, SOC_max_ev, C_ev, P_nom_ev,
                   P_max_hp, P_max_gen, P_nom_pv)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "results"


def check_res(res):
    eps = 1e-3
    errors = 0

    for t in range(time_steps):
        # Power balance
        imbalance = (res.P_pv[t] + res.P_gen[t]
                     - res.P_bss[t] - res.P_ev[t]
                     - res.P_load[t] - res.P_hp[t])
        if abs(imbalance) >= eps:
            print(f"[t={t}] Power balance error: {imbalance:.4f} kW")
            errors += 1

        # PV curtailment
        if res.P_pv[t] > res.P_pv_max[t] + eps:
            print(f"[t={t}] PV exceeds available: {res.P_pv[t]:.3f} > {res.P_pv_max[t]:.3f}")
            errors += 1

        # Battery SOC bounds
        soc_bss = res.SOC_bss[t] / C_bss
        if soc_bss < SOC_min_bss - eps or soc_bss > SOC_max_bss + eps:
            print(f"[t={t}] BSS SOC out of bounds: {soc_bss:.3f}")
            errors += 1

        # Battery power bounds
        if abs(res.P_bss[t]) > P_nom_bss + eps:
            print(f"[t={t}] BSS power out of bounds: {res.P_bss[t]:.3f}")
            errors += 1

        # EV bounds (only when connected)
        if res.EV_connected[t]:
            soc_ev = res.SOC_ev[t] / C_ev
            if soc_ev < SOC_min_ev - eps or soc_ev > SOC_max_ev + eps:
                print(f"[t={t}] EV SOC out of bounds: {soc_ev:.3f}")
                errors += 1
            if abs(res.P_ev[t]) > P_nom_ev + eps:
                print(f"[t={t}] EV power out of bounds: {res.P_ev[t]:.3f}")
                errors += 1

        # EV not connected -> no power
        if not res.EV_connected[t] and abs(res.P_ev[t]) > eps:
            print(f"[t={t}] EV power while disconnected: {res.P_ev[t]:.3f}")
            errors += 1

        # HP power bounds
        if res.P_hp[t] < -eps or res.P_hp[t] > P_max_hp + eps:
            print(f"[t={t}] HP power out of bounds: {res.P_hp[t]:.3f}")
            errors += 1

        # Generator bounds
        if res.P_gen[t] < -eps or res.P_gen[t] > P_max_gen + eps:
            print(f"[t={t}] Generator out of bounds: {res.P_gen[t]:.3f}")
            errors += 1

    if errors == 0:
        print("All constraint checks passed.")
    else:
        print(f"{errors} constraint violation(s) detected.")


def print_res(res):
    E_pv   = np.sum(res.P_pv)  * delta_t
    E_gen  = np.sum(res.P_gen) * delta_t
    E_load = np.sum(res.P_load)* delta_t
    E_hp   = np.sum(res.P_hp)  * delta_t
    E_curt = np.sum(np.maximum(res.P_pv_max - res.P_pv, 0)) * delta_t
    E_bss_ch  = np.sum(np.maximum( res.P_bss, 0)) * delta_t
    E_bss_dis = np.sum(np.maximum(-res.P_bss, 0)) * delta_t
    E_ev_ch   = np.sum(np.maximum( res.P_ev,  0)) * delta_t
    E_ev_dis  = np.sum(np.maximum(-res.P_ev,  0)) * delta_t

    print("\n" + "="*50)
    print("  SIMULATION RESULTS SUMMARY")
    print("="*50)
    print(f"  PV energy produced   : {E_pv:8.2f} kWh")
    print(f"  PV energy curtailed  : {E_curt:8.2f} kWh")
    print(f"  Generator energy     : {E_gen:8.2f} kWh")
    print(f"  Load consumed        : {E_load:8.2f} kWh")
    print(f"  HP consumed          : {E_hp:8.2f} kWh")
    print(f"  BSS charged          : {E_bss_ch:8.2f} kWh")
    print(f"  BSS discharged       : {E_bss_dis:8.2f} kWh")
    print(f"  EV charged           : {E_ev_ch:8.2f} kWh")
    print(f"  EV discharged        : {E_ev_dis:8.2f} kWh")
    print(f"  BSS final SOC        : {res.SOC_bss[-1]/C_bss*100:7.1f} %")
    print(f"  EV  final SOC        : {res.SOC_ev[-1]/C_ev*100:7.1f} %")
    print(f"  Indoor temp range    : [{np.min(res.T_hp[1:]):.1f}, {np.max(res.T_hp[1:]):.1f}] C")
    print("="*50 + "\n")


def plot_res(res):
    """Save the four-panel scenario plot and return its path."""
    t = res.t
    fig, axes = plt.subplots(4, 1, figsize=(12, 14), sharex=True)

    # Power flows
    ax = axes[0]
    ax.plot(t, res.P_pv_max, '--', color='gold',   lw=1.2, label='PV available')
    ax.plot(t, res.P_pv,     '-',  color='orange', lw=1.5, label='PV used')
    ax.plot(t, res.P_gen,    '-',  color='red',    lw=1.5, label='Generator')
    ax.plot(t, res.P_load,   '-',  color='black',  lw=1.5, label='Load')
    ax.plot(t, res.P_hp,     '-',  color='purple', lw=1.2, label='Heat pump')
    ax.set_ylabel('Power [kW]')
    ax.set_title('Electrical Power Flows')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Battery & EV power
    ax = axes[1]
    ax.plot(t, res.P_bss, '-', color='steelblue', lw=1.5, label='BSS (+charge/-discharge)')
    ax.plot(t, res.P_ev,  '-', color='green',     lw=1.5, label='EV  (+charge/-discharge)')
    ax.axhline(0, color='gray', lw=0.8, ls='--')
    ax.set_ylabel('Power [kW]')
    ax.set_title('Battery & EV Power')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # State of charge
    ax = axes[2]
    ax.plot(t, res.SOC_bss / C_bss * 100, '-',  color='steelblue', lw=1.5, label='BSS SOC')
    ax.plot(t, res.SOC_ev  / C_ev  * 100, '-',  color='green',     lw=1.5, label='EV SOC')
    ax.fill_between(t, 0, res.EV_connected.astype(float)*100,
                    alpha=0.08, color='green', label='EV connected')
    ax.axhline(20, color='gray', lw=0.8, ls='--')
    ax.axhline(85, color='gray', lw=0.8, ls='--')
    ax.set_ylabel('SOC [%]')
    ax.set_ylim(0, 100)
    ax.set_title('State of Charge')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Temperature
    ax = axes[3]
    ax.plot(t, res.T_hp,  '-',  color='tomato',  lw=1.5, label='Indoor temp')
    ax.plot(t, res.T_set, '--', color='darkred', lw=1.2, label='Setpoint')
    ax.fill_between(t, res.T_set - 2, res.T_set + 2,
                    alpha=0.15, color='red', label='+/-2 C comfort band')
    ax.set_ylabel('Temperature [C]')
    ax.set_xlabel('Time [h]')
    ax.set_title('Indoor Temperature vs Setpoint')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RESULTS_DIR / f"{res.controller_name}_{res.scenario}.png"
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"Plot saved to {output_path}")
    return output_path
