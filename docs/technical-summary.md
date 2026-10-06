# Technical summary

## Physical system

The simulated residential microgrid contains five controllable or exogenous
energy elements:

1. photovoltaic generation with a 10 kW nominal cap;
2. a 2-10 kW dispatchable generator;
3. a 40 kWh stationary battery with 10 kW bidirectional power;
4. a 60 kWh EV battery with 10 kW bidirectional power and an 80% departure
   target; and
5. a 5 kW electrical heat pump with coefficient of performance 2.5.

Building electrical load, PV availability, EV connection state, envelope heat
loss and temperature setpoint are supplied at 1.5-minute intervals for four
24-hour scenarios.

## State equations and sign conventions

The simulator represents battery and EV state internally as stored energy in
kWh, despite naming the arrays `SOC_bss` and `SOC_ev`. For either storage
device, positive power means charging and negative power means discharging.
With capacity `C`, efficiency `eta`, interval `dt` and signed power `P`, the
implemented state update is equivalent to:

```text
E[k] = E[k-1] + dt * eta * max(P, 0) + dt / eta * min(P, 0)
```

The indoor-temperature state follows the lumped model:

```text
T[k] = T[k-1] + dt * (COP * P_hp[k] - P_loss[k]) / C_hp
```

Here `P_hp` is electrical power, `COP * P_hp` is delivered heat and `P_loss`
is thermal envelope loss. Units are dimensionally consistent if `C_hp` is in
kWh/K and the power terms are in kW.

## Rule-based method

The controller first determines a heat-pump command from the setpoint error,
thermal loss and a 0.25 K deadband. It calculates a just-in-time EV charging
rate from the remaining connection duration. Available PV then supplies the
minimum demand.

For a PV surplus, the controller accelerates EV charging, may use the stationary
battery to support extra EV charging, charges the battery with remaining PV,
and finally tops the EV above its target if both surplus and battery headroom
conditions allow. For a deficit, the stationary battery discharges subject to
a 35% hysteresis threshold while the generator was previously operating. The
EV can discharge down to its 80% target, and the generator supplies the final
shortfall in whole-kilowatt steps.

## Optimization method

At each interval, Pyomo selects nonnegative PV, generator, charging,
discharging and heat-pump powers plus binary generator, BSS and EV modes. The
objective combines:

- generator energy;
- curtailed PV energy;
- positive and negative temperature-deviation slack;
- generator switching and change in output;
- battery charging/discharging throughput; and
- change in EV charging power.

Constraints enforce power balance, PV availability, storage power and SOC
bounds, EV connection, mutually exclusive charge/discharge modes, an EV
minimum charging rate, heat-pump power, a one-step temperature-rise bound, and
generator minimum/maximum output. A 30% battery threshold is used in the
optimizer's hysteresis state.

The mathematical program is mixed-integer linear. It is not time-indexed and
does not optimize a full forecast horizon. Future information enters only
through the EV's remaining connection time.

## Scenarios

- **S1 Standard:** moderate PV, standard load and a long EV connection window.
- **S2 High PV:** doubled PV availability and a later EV window.
- **S3 Low PV:** one-third of S1 PV and an initially connected, low-SOC EV.
- **S4 Tight Window:** high PV with a shorter EV connection period and higher
  load energy.

These labels are inferred from the report and the supplied profiles; the
source folder contains no formal scenario-definition document.

## Performance indicators

The software reports PV energy used and curtailed, generator energy, electrical
load, heat-pump energy, charge/discharge throughput, final storage SOC and
indoor-temperature range. `check_res` also checks instantaneous power balance,
PV availability, SOC and power bounds, EV connection, heat-pump power and
generator power.

## Reported conclusions

The report states that both controllers serve load and achieve 80% final EV
SOC in all scenarios. It portrays the rule-based controller as a reliable
baseline and the optimizer as smoother and more efficient, especially when PV
or the EV window creates timing constraints. These optimizer superiority
claims were not confirmed by execution and are weakened by the one-step model
identified in the code.
