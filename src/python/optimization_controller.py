"""One-step Pyomo mixed-integer microgrid controller.

The model is rebuilt for each scenario and updated at each simulation time
step.  It minimizes weighted generator use, PV curtailment, comfort deviation,
switching/ramping proxies, battery throughput and EV charging variation.

Run ``python src/python/optimization_controller.py --scenario S1`` from the
repository root.  A working Gurobi or GLPK solver is required.
"""

import argparse

from param import delta_t
from param import (
    P_nom_pv, P_max_gen, P_min_gen,
    C_bss, SOC_min_bss, SOC_max_bss, eff_bss, P_nom_bss,
    C_ev, eff_ev, SOC_min_ev, SOC_max_ev, P_nom_ev, SOC_target_ev,
    P_max_hp, COP_hp, C_hp, delta_T_max
)

from pyomo.environ import (
    ConcreteModel, Param, Var, Objective, Constraint,
    NonNegativeReals, Binary, minimize,
    SolverFactory, SolverStatus
)

import run


# Cost / penalty weights

PI_gen         = 1.0
PI_curt        = 0.05     # reduced so HP is not used as artificial PV dump
PI_T           = 5.0

PI_gen_switch  = 0.5
PI_gen_ramp    = 0.25
PI_bss_cycle   = 0.02
PI_ev_smooth   = 0.05

battery_threshold = 0.3
HP_DEADBAND = 0.25


# Model creation

def create_model():
    """Create the scalar, single-time-step Pyomo optimization model."""
    model = ConcreteModel()

# Mutable parameters
    model.SOC_ev            = Param(mutable=True, initialize=0.5)
    model.SOC_bss           = Param(mutable=True, initialize=0.5)
    model.P_load            = Param(mutable=True, initialize=0.0)

    model.P_pv_max          = Param(mutable=True, initialize=0.0)
    model.P_pv_available    = Param(mutable=True, initialize=0.0)

    model.EV_connected      = Param(mutable=True, within=Binary, initialize=0)
    model.EV_time_remaining = Param(mutable=True, initialize=0.0)

    model.Pgen_prev         = Param(mutable=True, initialize=0.0)
    model.gen_prev_status   = Param(mutable=True, within=Binary, initialize=0)

    model.P_loss            = Param(mutable=True, initialize=0.0)
    model.T_set             = Param(mutable=True, initialize=20.0)
    model.T_hp              = Param(mutable=True, initialize=20.0)

    model.hp_allowed        = Param(mutable=True, within=Binary, initialize=1)
    model.P_hp_ub           = Param(mutable=True, initialize=0.0)

    model.bss_lock          = Param(mutable=True, within=Binary, initialize=0)

    model.P_ev_charge_prev  = Param(mutable=True, initialize=0.0)

# Decision variables
    model.P_pv            = Var(within=NonNegativeReals)
    model.P_gen           = Var(within=NonNegativeReals)

    model.P_charge_bss    = Var(within=NonNegativeReals)
    model.P_discharge_bss = Var(within=NonNegativeReals)

    model.P_charge_ev     = Var(within=NonNegativeReals)
    model.P_discharge_ev  = Var(within=NonNegativeReals)

    model.P_hp            = Var(within=NonNegativeReals)

    model.T_slack_pos     = Var(within=NonNegativeReals)
    model.T_slack_neg     = Var(within=NonNegativeReals)

    model.gen_status      = Var(within=Binary, initialize=0)
    model.bss_status      = Var(within=Binary, initialize=0)
    model.ev_status       = Var(within=Binary, initialize=0)

    model.gen_switch      = Var(within=Binary, initialize=0)
    model.gen_ramp        = Var(within=NonNegativeReals, initialize=0)

    model.ev_ramp         = Var(within=NonNegativeReals, initialize=0)

 # Objective
    model.objective = Objective(
        sense=minimize,
        expr=(
            PI_gen * model.P_gen * delta_t
            + PI_curt * (model.P_pv_available - model.P_pv) * delta_t
            + PI_T * (model.T_slack_pos + model.T_slack_neg) * delta_t
            + PI_gen_switch * model.gen_switch
            + PI_gen_ramp * model.gen_ramp
            + PI_bss_cycle * (
                model.P_charge_bss + model.P_discharge_bss
            ) * delta_t
            + PI_ev_smooth * model.ev_ramp
        )
    )

# Power balance
    model.P_bal_cstr = Constraint(
        expr=(
            model.P_pv
            + model.P_gen
            + model.P_discharge_bss
            + model.P_discharge_ev
            ==
            model.P_load
            + model.P_hp
            + model.P_charge_bss
            + model.P_charge_ev
        )
    )

  # PV constraint
    model.pv_max_cstr = Constraint(
        expr=model.P_pv <= model.P_pv_available
    )

 # Battery constraints
    model.bss_ch_max = Constraint(
        expr=model.P_charge_bss <= P_nom_bss * model.bss_status
    )

    model.bss_dis_max = Constraint(
        expr=model.P_discharge_bss <= P_nom_bss * (1 - model.bss_status)
    )

    model.hysteresis_constraint = Constraint(
        expr=model.bss_status >= model.bss_lock
    )

    model.bss_soc_min = Constraint(
        expr=(
            model.SOC_bss
            + delta_t * (
                model.P_charge_bss * eff_bss
                - model.P_discharge_bss / eff_bss
            ) / C_bss
            >= SOC_min_bss
        )
    )

    model.bss_soc_max = Constraint(
        expr=(
            model.SOC_bss
            + delta_t * (
                model.P_charge_bss * eff_bss
                - model.P_discharge_bss / eff_bss
            ) / C_bss
            <= SOC_max_bss
        )
    )

   # EV constraints
    model.ev_ch_conn = Constraint(
        expr=model.P_charge_ev <= P_nom_ev * model.EV_connected * model.ev_status
    )

    model.ev_dis_conn = Constraint(
        expr=model.P_discharge_ev <= P_nom_ev * model.EV_connected * (1 - model.ev_status)
    )

    model.ev_soc_min = Constraint(
        expr=(
            model.SOC_ev
            + delta_t * (
                model.P_charge_ev * eff_ev
                - model.P_discharge_ev / eff_ev
            ) / C_ev
            >= SOC_min_ev * model.EV_connected
            + model.SOC_ev * (1 - model.EV_connected)
        )
    )

    model.ev_soc_max = Constraint(
        expr=(
            model.SOC_ev
            + delta_t * (
                model.P_charge_ev * eff_ev
                - model.P_discharge_ev / eff_ev
            ) / C_ev
            <= SOC_max_ev
        )
    )

    model.ev_ramp_up = Constraint(
        expr=model.ev_ramp >= model.P_charge_ev - model.P_ev_charge_prev
    )

    model.ev_ramp_down = Constraint(
        expr=model.ev_ramp >= model.P_ev_charge_prev - model.P_charge_ev
    )

    model.ev_target_cstr = Constraint(
        expr=model.P_charge_ev >= 0.0
    )

  # Heat pump constraints
    model.hp_max = Constraint(
        expr=model.P_hp <= model.P_hp_ub
    )

    model.T_slack_pos_cstr = Constraint(
        expr=(
            model.T_slack_pos
            >= (
                model.T_hp
                + delta_t * (model.P_hp * COP_hp - model.P_loss) / C_hp
            )
            - model.T_set
        )
    )

    model.T_slack_neg_cstr = Constraint(
        expr=(
            model.T_slack_neg
            >= model.T_set
            - (
                model.T_hp
                + delta_t * (model.P_hp * COP_hp - model.P_loss) / C_hp
            )
        )
    )

    model.T_delta_max = Constraint(
        expr=(
            model.T_hp
            + delta_t * (model.P_hp * COP_hp - model.P_loss) / C_hp
            <= model.T_hp + delta_T_max
        )
    )

  # Generator constraints
    model.gen_on_max = Constraint(
        expr=model.P_gen <= P_max_gen * model.gen_status
    )

    model.gen_on_min = Constraint(
        expr=model.P_gen >= P_min_gen * model.gen_status
    )

    model.gen_switch_up = Constraint(
        expr=model.gen_switch >= model.gen_status - model.gen_prev_status
    )

    model.gen_switch_down = Constraint(
        expr=model.gen_switch >= model.gen_prev_status - model.gen_status
    )

    model.gen_ramp_up = Constraint(
        expr=model.gen_ramp >= model.P_gen - model.Pgen_prev
    )

    model.gen_ramp_down = Constraint(
        expr=model.gen_ramp >= model.Pgen_prev - model.P_gen
    )

    return model


# Solver

def solve_model(model):
    """Solve with the first available solver in the Gurobi/GLPK list."""
    for solver_name in ["gurobi", "glpk"]:
        solver = SolverFactory(solver_name)

        if solver.available():
            results = solver.solve(model)

            if results.solver.status not in [SolverStatus.ok, SolverStatus.warning]:
                print(f"Solver {solver_name} status: {results.solver.status}")

            return

    print("WARNING: No suitable solver found.")


# Model update

def update_model(
    model,
    SOC_bss,
    SOC_ev,
    P_load,
    P_pv_max,
    EV_connected,
    EV_remaining_time,
    P_gen_prev,
    P_loss,
    T_set,
    T_hp
):
    """Update mutable model parameters from the current simulation state."""

# Basic state update
    model.SOC_ev.set_value(SOC_ev)
    model.SOC_bss.set_value(SOC_bss)

    model.P_load.set_value(P_load)
    model.P_pv_max.set_value(P_pv_max)
    model.P_pv_available.set_value(min(P_pv_max, P_nom_pv))

    model.EV_connected.set_value(int(EV_connected))
    model.EV_time_remaining.set_value(EV_remaining_time)

    model.Pgen_prev.set_value(P_gen_prev)

    model.P_loss.set_value(P_loss)
    model.T_set.set_value(T_set)
    model.T_hp.set_value(T_hp)

  # Generator previous status
    prev_status = 1 if P_gen_prev > 1e-6 else 0
    model.gen_prev_status.set_value(prev_status)

  # Heat pump rule-based upper bound
# This code wlil prevents the optimizer from using HP as a PV dump load.

    if P_loss <= 0:
        hp_allowed = 0
        P_hp_ub = 0.0

    elif T_hp > T_set + HP_DEADBAND:
        hp_allowed = 0
        P_hp_ub = 0.0

    else:
        hp_allowed = 1

        P_hp_target = (
            (T_set - T_hp) * C_hp / (COP_hp * delta_t)
            + P_loss / COP_hp
        )

        P_hp_rate_limit = (
            delta_T_max * C_hp / delta_t
            + P_loss
        ) / COP_hp

        P_hp_ub = min(
            P_max_hp,
            P_hp_rate_limit,
            max(0.0, P_hp_target)
        )

    model.hp_allowed.set_value(hp_allowed)
    model.P_hp_ub.set_value(P_hp_ub)

# Battery hysteresis lock
    current_lock = model.bss_lock.value if model.bss_lock.value is not None else 0

    if current_lock == 1:
        if SOC_bss >= battery_threshold:
            model.bss_lock.set_value(0)
        else:
            model.bss_lock.set_value(1)
    else:
        if SOC_bss <= SOC_min_bss:
            model.bss_lock.set_value(1)
        else:
            model.bss_lock.set_value(0)

  # EV minimum charge rate to reach target before departure
    if EV_connected and EV_remaining_time > 1e-6 and SOC_ev < SOC_target_ev:
        needed_energy = max(0.0, (SOC_target_ev - SOC_ev) * C_ev)

        P_min_needed = needed_energy / (eff_ev * EV_remaining_time)

        P_min_needed = min(
            P_nom_ev,
            P_min_needed,
            (SOC_max_ev - SOC_ev) * C_ev / (delta_t * eff_ev)
        )

        P_min_needed = max(0.0, P_min_needed)

    else:
        P_min_needed = 0.0

    model.ev_target_cstr.set_value(
        model.P_charge_ev >= int(EV_connected) * P_min_needed
    )

    return model

# Control decision

def control_decision(
    P_load,
    P_pv_max,
    EV_connected,
    EV_remaining_time,
    P_gen_prev,
    SOC_bss,
    SOC_ev,
    P_loss,
    T_set,
    T_hp,
    model
):
    """Solve one control interval and return five power commands in kW."""

    model = update_model(
        model,
        SOC_bss,
        SOC_ev,
        P_load,
        P_pv_max,
        EV_connected,
        EV_remaining_time,
        P_gen_prev,
        P_loss,
        T_set,
        T_hp
    )

    solve_model(model)

    try:
        P_pv = model.P_pv.value
        P_gen = model.P_gen.value

        P_bss = model.P_charge_bss.value - model.P_discharge_bss.value
        P_ev = model.P_charge_ev.value - model.P_discharge_ev.value

        P_hp = model.P_hp.value

        if any(v is None for v in [P_pv, P_gen, P_bss, P_ev, P_hp]):
            raise ValueError("None in solution")

        model.P_ev_charge_prev.set_value(max(0.0, model.P_charge_ev.value))

    except Exception as e:
        print(f"WARNING: Problem with solution: {e}")

        P_pv = 0.0
        P_gen = 0.0
        P_bss = 0.0
        P_ev = 0.0
        P_hp = 0.0

        model.P_ev_charge_prev.set_value(0.0)

    return P_pv, P_gen, P_bss, P_ev, P_hp


def main(scenarios=None):
    """Run the requested optimization-based scenarios."""
    scenarios = scenarios or ["S1", "S2", "S3", "S4"]
    for scenario in scenarios:
        print("\n" + "=" * 70)
        print(f"Running optimization-based controller for {scenario}")
        print("=" * 70)

        # A fresh model prevents state from carrying between scenarios.
        model = create_model()
        run.run_sim(
            control_decision,
            scenario,
            model,
            controller_name="optimization",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Pyomo microgrid controller."
    )
    parser.add_argument(
        "--scenario",
        nargs="+",
        choices=["S1", "S2", "S3", "S4"],
        default=["S1", "S2", "S3", "S4"],
        help="Scenario(s) to run; default: all four.",
    )
    args = parser.parse_args()
    main(args.scenario)
