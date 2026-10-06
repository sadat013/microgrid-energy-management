"""Reactive rule-based energy-management controller.

The controller prioritizes heat-pump comfort and required EV charging, uses PV
when available, dispatches the stationary battery, permits EV-to-home support
above the EV target SOC, and starts the generator for any remaining deficit.

Run ``python src/python/rule_based_controller.py --scenario S1`` from the
repository root.  Omitting ``--scenario`` preserves the submitted script's
default of Scenario 4.
"""

import argparse
import math
from param import delta_t, time_steps
from param import (
    P_nom_pv, P_max_gen, P_min_gen,
    C_bss, SOC_min_bss, SOC_max_bss, eff_bss, P_nom_bss,
    C_ev, eff_ev, SOC_min_ev, SOC_max_ev, P_nom_ev, SOC_target_ev,
    P_max_hp, COP_hp, C_hp, delta_T_max
)
import run


BATTERY_THRESHOLD = 0.35


def reset_gen_state():
    """Compatibility hook retained from the submitted controller."""
    pass


def control_decision(P_load, P_pv_max, EV_connected, EV_remaining_time,
                     P_gen_prev, SOC_bss, SOC_ev, P_loss, T_set, T_hp, model=None):

     # 1. Heat pump logic

    HP_DEADBAND = 0.25

    if P_loss <= 0:
        P_hp = 0.0
    elif T_hp > T_set + HP_DEADBAND:
        P_hp = 0.0
    else:
        P_hp_target = (T_set - T_hp) * C_hp / (COP_hp * delta_t) + P_loss / COP_hp
        P_hp_rate_limit = (delta_T_max * C_hp / delta_t + P_loss) / COP_hp
        P_hp = min(P_max_hp, P_hp_rate_limit, max(0.0, P_hp_target))

    # 2. Initialize outputs

    P_pv = 0.0
    P_bss = 0.0
    P_gen = 0.0
    P_ev = 0.0

    # 3. Available PV

    P_pv_available = min(P_pv_max, P_nom_pv)

    # 4. EV charging requirement to reach target before departure

    if EV_connected and SOC_ev < SOC_target_ev and EV_remaining_time > 1e-9:
        min_P_ev = (SOC_target_ev - SOC_ev) * C_ev / ((EV_remaining_time + 1e-9) * eff_ev)
        max_P_ev = min(
            P_nom_ev,
            (SOC_target_ev - SOC_ev) * C_ev / (delta_t * eff_ev),
            (SOC_max_ev - SOC_ev) * C_ev / (delta_t * eff_ev)
        )
        min_P_ev = max(0.0, min(min_P_ev, max_P_ev))
        add_P_ev = max(0.0, max_P_ev - min_P_ev)
    else:
        min_P_ev = 0.0
        max_P_ev = 0.0
        add_P_ev = 0.0
        P_ev = 0.0

    # 5. Total demand includes load + HP + minimum EV charging
    P_ev += min_P_ev
    total_min_demand = P_load + P_hp + min_P_ev
    total_max_demand = P_load + P_hp + max_P_ev

   # 6. Surplus case: PV can cover minimum demand
    if P_pv_available >= total_min_demand:
        surplus = P_pv_available - total_min_demand

        # A. Use PV surplus to charge EV faster up to max_P_ev
        if EV_connected and EV_remaining_time > 1e-9 and add_P_ev > 0.0:
            EV_increment_from_pv = min(surplus, add_P_ev)
            P_ev += EV_increment_from_pv
            surplus -= EV_increment_from_pv

        # B. If PV surplus was not enough, BSS may support extra EV charging
        remaining_extra_ev = max(0.0, max_P_ev - P_ev)
        if EV_connected and EV_remaining_time > 1e-9 and remaining_extra_ev > 1e-9:
            max_batt_discharge = max(
                0.0,
                min(
                    P_nom_bss,
                    (SOC_bss - SOC_min_bss) * C_bss * eff_bss / delta_t
                )
            )

            ev_from_bss = min(remaining_extra_ev, max_batt_discharge)
            if ev_from_bss > 1e-9:
                P_ev += ev_from_bss
                P_bss -= ev_from_bss

        # C. Charge the battery with remaining PV surplus
        if surplus > 1e-9:
            max_batt_charge = max(
                0.0,
                min(
                    P_nom_bss,
                    (SOC_max_bss - SOC_bss) * C_bss / (delta_t * eff_bss)
                )
            )
            P_bss_charge = min(surplus, max_batt_charge)
            P_bss += P_bss_charge
            surplus -= P_bss_charge

        # D. If battery is full, use remaining PV to top up EV toward SOC_max
        if (surplus > 1e-9 and EV_connected and EV_remaining_time > 1e-9
                and SOC_ev >= SOC_target_ev and SOC_ev < SOC_max_ev
                and SOC_bss >= SOC_max_bss):
            EV_extra_capacity = (SOC_max_ev - SOC_ev) * C_ev / (delta_t * eff_ev)
            EV_extra_charge_input = min(surplus, EV_extra_capacity, P_nom_ev - max(P_ev, 0.0))
            EV_extra_charge_input = max(0.0, EV_extra_charge_input)
            P_ev += EV_extra_charge_input
            surplus -= EV_extra_charge_input

        P_pv = P_pv_available - surplus

     # 7. Deficit case: PV cannot cover minimum demand
    else:
        min_deficit = total_min_demand - P_pv_available
        max_deficit = total_max_demand - P_pv_available
        P_pv = P_pv_available

        # Battery discharge allowed with hysteresis
        if ((P_gen_prev == 0 and SOC_bss >= SOC_min_bss) or
                (P_gen_prev != 0 and SOC_bss >= BATTERY_THRESHOLD)):
            max_batt_discharge = max(
                0.0,
                min(
                    P_nom_bss,
                    (SOC_bss - SOC_min_bss) * C_bss * eff_bss / delta_t
                )
            )
        else:
            max_batt_discharge = 0.0

        # A. Battery can fully cover minimum deficit
        if max_batt_discharge >= min_deficit:
            P_gen = 0.0

            if EV_connected and SOC_ev < SOC_target_ev:
                P_available = min(max_deficit, max_batt_discharge)
                P_bss = -P_available
                P_ev += max(0.0, P_available - min_deficit)
            else:
                P_bss = -min_deficit

        # B. Battery cannot fully cover minimum deficit
        else:
            P_bss = -max_batt_discharge
            remaining_demand = min_deficit - max_batt_discharge

            # EV above target can support house through V2H
            if EV_connected and SOC_ev > SOC_target_ev:
                max_ev_discharge = min(
                    P_nom_ev,
                    (SOC_ev - SOC_target_ev) * C_ev * eff_ev / delta_t
                )

                if max_ev_discharge >= remaining_demand:
                    P_ev = -remaining_demand
                    P_gen = 0.0
                    remaining_demand = 0.0
                else:
                    P_ev = -max_ev_discharge
                    remaining_demand -= max_ev_discharge
                    P_gen = max(P_gen_prev, math.ceil(max(remaining_demand, P_min_gen)))
                    P_gen = min(P_gen, P_max_gen)
            else:
                P_gen = max(P_gen_prev, math.ceil(max(remaining_demand, P_min_gen)))
                P_gen = min(P_gen, P_max_gen)

            # Generator surplus charges battery
            if P_gen > remaining_demand:
                generator_surplus = P_gen - remaining_demand
                max_batt_charge = max(
                    0.0,
                    min(
                        P_nom_bss,
                        (SOC_max_bss - SOC_bss) * C_bss / (delta_t * eff_bss)
                    )
                )
                P_batt_charge = min(generator_surplus, max_batt_charge)
                P_bss = P_bss + P_batt_charge

    return P_pv, P_gen, P_bss, P_ev, P_hp


def main(scenarios=None):
    """Run the requested rule-based scenarios."""
    scenarios = scenarios or ["S4"]
    for scenario in scenarios:
        reset_gen_state()
        print(f"\n{'=' * 60}")
        print(f"  SCENARIO {scenario}")
        print(f"{'=' * 60}")
        run.run_sim(
            control_decision,
            scenario,
            controller_name="rule_based",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the rule-based microgrid controller."
    )
    parser.add_argument(
        "--scenario",
        nargs="+",
        choices=["S1", "S2", "S3", "S4"],
        default=["S4"],
        help="Scenario(s) to run; default: S4.",
    )
    args = parser.parse_args()
    main(args.scenario)
