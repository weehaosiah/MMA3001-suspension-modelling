# Following one bump through the model

This learning note explains the nominal code and result. It is not assessed report
prose, and reading it does not establish that the student can yet explain the model
independently. See `README.md` for the command to reproduce the nominal case.

## 1. Tell the model what the road does

`road_height` in `quarter_car.py` returns the road height at a supplied time.
The road starts at zero, reaches 50 mm at 0.25 s, and returns to zero at 0.50 s.
It remains flat after that. This is an input we prescribe, not a measured output.

The 50 mm road height is different from the suspension's movement: the wheel and
body both move, so neither is a fixed reference for the other.

## 2. Remember where both masses are and how fast they are moving

The **state** is a four-item array: `[zs, vs, zu, vu]`. An array is an ordered
collection of numbers. Here it contains the body position and velocity, followed
by the wheel position and velocity, all at the same instant.

Positions are measured from the statically loaded resting positions. Consequently
zero means no extra displacement from rest, not that the vehicle has no weight.
Both masses initially have zero dynamic displacement and zero velocity.

## 3. Turn movement into forces and accelerations

The function `rhs` calculates how the state is changing. It first forms:

```python
relative_displacement = zs - zu
relative_velocity = vs - vu
```

The spring force depends on relative displacement; the damper force depends on
relative velocity. The same suspension force acts in opposite directions on the
two masses. Dividing each mass's total dynamic force by its mass gives acceleration.
The return order is `[body velocity, body acceleration, wheel velocity, wheel acceleration]`.

For example, a 10 mm extension at nominal stiffness produces a 240 N spring-force
change. With zero relative velocity and a wheel at equilibrium on flat road, it
pulls the body down and the wheel up. This is a hand-check of signs and units, not
an extra measured simulation result.

## 4. Advance the complete state

`simulate` asks SciPy's RK45 method to advance all four quantities together.
RK45 uses several force calculations per step to estimate how the state evolves;
it adjusts its internal step sizes using an error estimate.

The calculation stops explicitly at bump exit and then resumes with the SAME
four numbers. It does not put the body or wheel back at rest. The road is flat,
but the masses still have velocity and the springs still store energy.

An **observation grid** is the set of times at which we inspect the computed
motion. It is separate from RK45's internal steps. We check both solver accuracy
and observation spacing because a coarse observation grid might miss a peak even
when the underlying trajectory is accurate.

## 5. Ask two different questions about the motion

The primary output is the largest absolute body-minus-wheel displacement across
the entire response, including after the bump. In the nominal case this is
40.571 mm, an extension near 0.442 s.

The post-bump maximum includes the exit instant. For this case it is 31.892 mm
at 0.50 s. The suspension later swings through compression before its oscillations
decay. Keeping only the maximum would hide this continuing motion.

Settling asks when the remaining relative displacement stays inside the chosen
small band. At the nominal +/-1 mm band, the final entry is approximately 1.769 s
from the start, or 1.269 s AFTER the 0.50 s bump exit. The first crossing of zero
does not count if the response subsequently leaves the band again. Being in the
band does not mean both masses are stationary.

## 6. Decide what evidence makes those numbers usable

The nominal checks compare tighter solver tolerances, closer observation times
and a longer run. They also check equilibrium, forces, complete state continuity,
positive tyre contact and decreasing energy after the bump.

The next verification extends these checks to nine combinations of stiffness and
damping, compares the taught RK4 method, and checks a simpler oscillator against
an exact formula. Those are checks of numerical implementation. They cannot show
that this generic linear model accurately represents a particular real car.

For learning, work through these prompts using the code and plot:

1. Why does the state include velocities as well as positions?
2. If body and wheel move upward by the same amount, what is the suspension travel?
3. Why can the suspension still oscillate after the road becomes flat?
4. Why would a 0.5 mm settling band usually give a longer time than a 2 mm band?
5. What could two numerical solvers agree on while both still being wrong about a real vehicle?

The prompts are for the student's own explanation; no answers or understanding
have been attributed to the student by the assistant.
