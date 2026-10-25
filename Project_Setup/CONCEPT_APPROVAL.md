# Suspension modelling concept approval draft

Revision: 001 | Updated: 2026-10-12 | Status: draft for student review; not submitted

This draft describes the adopted project design in the student's requested format. Scientific implementation and final evaluation are already complete; it does not authorise a new experiment or another use of the consumed final test.

---

Here’s my plan: modelling how a suspension responds to a road bump and checking whether machine learning can predict its maximum movement accurately and quickly.

**Dataset:**

400 simulated suspension setups from a quarter-car model: a simplified model of one corner of a vehicle, with a body mass, wheel mass, spring, damper and tyre. Fixed vehicle parameters come from [Soong et al. (2017)](https://doi.org/10.1371/journal.pone.0179485). Each setup crosses the same smooth, 50 mm bump over 0.50 seconds, with motion calculated for five seconds using the Runge–Kutta method, RK45. Calculations use SI units, with suspension movement reported in millimetres.

**Problem:**

Spring stiffness and damping affect how far a suspension moves and how long it continues oscillating after a bump. I’m investigating these effects and whether a model trained on simulated examples can predict peak movement without solving the motion equations for every new setup.

**Why it matters:**

Engineers need to compare suspension settings while managing movement and how quickly the response settles. This provides a manageable engineering application of machine learning, with a physical simulation available to check its predictions.

**Inputs:**

Spring stiffness from 18,000–30,000 N/m and damping coefficient from 1,594.8–2,658.0 N·s/m. Body mass, wheel mass, tyre stiffness and the bump remain fixed. These ranges are study choices around the reference setup, not measured Ferrari 296 settings.

**Outputs:**

The main prediction is the largest suspension compression or extension from its resting position, measured as relative movement between the body and wheel. Supporting simulation analysis examines movement after the bump and the time taken to stay within ±1 mm of the resting position. This settling band is a study tolerance, not a safety standard. Settling time is not an additional machine-learning target.

**Baseline method:**

Multiple linear regression: a simple equation predicting peak movement from spring stiffness and damping. It provides an easy-to-explain starting point for assessing whether a more flexible model adds value.

**Alternative method:**

Support-vector regression with a radial-basis-function kernel, which can learn a curved relationship between the inputs and peak movement. The comparison considers prediction error, calculation time and ease of explanation.

**Validation:**

The numerical simulation is checked against a simplified case with a known mathematical solution, another Runge–Kutta method, RK4, and finer numerical settings. The dataset split uses 225 training setups, 75 validation setups for choosing settings, and 100 separate final-test setups. After choices are fixed, both models are refitted on the same 300 development setups and evaluated once on the final test. Errors include typical error, worst-case error and underprediction. This checks agreement with the simulator, not a real car.

**Sensitivity and performance:**

I examine changes across the spring and damping ranges, and check sensitivity to numerical settings, simulation duration and the settling tolerance. Timing compares simulation and regression predictions for the same peak-movement output, with data-generation and training costs reported separately.

**Limitations:**

The model represents one generic vehicle corner and one bump, with linear springs and dampers and assumed tyre contact. It omits bump stops, body pitch and roll, and aerodynamics. It is not calibrated to ACC telemetry or a Ferrari 296, and cannot establish real-car safety, comfort, grip or lap-time improvements. Predictions outside the studied ranges are not validated.
