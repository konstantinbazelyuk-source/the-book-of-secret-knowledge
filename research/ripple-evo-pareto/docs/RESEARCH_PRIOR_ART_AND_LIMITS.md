# Ripple EvoPareto v1.3 — research, engineering standards and prior art

**Citation status:** These are bibliographic and design-context sources. Code in this release is separately authored. Patent publication does **not** mean free-to-use. The legal scope, jurisdiction, expiration, and licensing of each patent require qualified review before commercial manufacturing.

## Peer-reviewed mathematical methods

- Deb, Pratap, Agarwal, Meyarivan (2002), *A Fast and Elitist Multiobjective Genetic Algorithm: NSGA-II*, IEEE Transactions on Evolutionary Computation 6(2), 182–197, DOI 10.1109/4235.996017. Inspired Pareto dominance, elitist survival and normalized crowding. **The code is an independently implemented NSGA-II-inspired algorithm**, not a certified implementation of every detail of the paper.
  https://doi.org/10.1109/4235.996017
- Peng et al. (2018), *Sim-to-Real Transfer of Robotic Control with Dynamics Randomization*, ICRA, DOI 10.1109/ICRA.2018.8460528. Basis for testing varying actuator lag/rate. Paper demonstrates a robotic arm, not this eight-legged robot.
  https://xbpeng.github.io/projects/SimToReal/
- Tan et al. (2018), *Sim-to-Real: Learning Agile Locomotion for Quadruped Robots*, arXiv:1804.10332. Shows why measured actuator characteristics and latency must be included in a higher-fidelity model.
  https://arxiv.org/abs/1804.10332
- Muratore et al. (2018), *Domain Randomization for Simulation-Based Policy Optimization with Transferability Assessment*, CoRL. Warns about simulation optimization bias; mandates stress tests and physical measurements.
  https://proceedings.mlr.press/v87/muratore18a.html

## U.S. patent publications (prior-art study, not copied designs)

- US 12,128,570 B2, *Handling gait disturbances with asynchronous timing* (Boston Dynamics). Relevant to handling unexpected swing timing. Our v1.3 does not implement this claimed asynchronous method.
  https://patents.google.com/patent/US12128570B2/en
- US 12,139,217 B2, *Slip detection for robotic locomotion* (Boston Dynamics). Reinforces separating actual measured foot slip from our foot-error simulation proxy. We do NOT implement or claim slip sensing.
  https://patents.google.com/patent/US12139217B2/en
- US 11,771,290 B2 / US20200367715A1, *Sensors for an autonomous cleaning robot* (iRobot). Existing prior art for cliffs and floor navigation. SpiderScan v1.3 does not have a cleaning or cliff-detection deployment claim.
  https://patents.google.com/patent/US20200367715A1/en
- US 11,614,746 B2 / US20190212752A1, *Mobile cleaning robot teaming and persistent mapping* (iRobot). Context for shared maps; no patented mapping method is copied in EvoPareto.
  https://patents.google.com/patent/US20190212752A1/en

Primary U.S. patent search belongs with the USPTO: https://www.uspto.gov/patents/search/patent-public-search. The FBI is not the U.S. patent registry.

## FBI forensic image reference

- FBI Handbook of Forensic Services, footwear/tire impression imaging. Recommends low-angle lighting, a physical scale, careful file preservation. Relevant for **future** scanner input validation, not motor optimization.
  https://www.fbi.gov/file-repository/handbook-of-forensic-services-pdf.pdf

## Engineering program guidance

- NASA Software Engineering Handbook SWE-028, SWE-055, SWE-067: verification plan, distinguishing validation, requirements and explicit acceptance gates. We adopt traceability as a practice; this research project is **not NASA-accredited or certified**.
  https://swehb.nasa.gov/spaces/7150/pages/16450576/SWE-028+-+Verification+Planning

## Measurement and simulation limits

- All v1.3 scores use the inherited first-order motor model. This is not an accurate representation of torque, collisions, Coulomb friction, inertia, slopes, deformable soils, actual ground contact, sensor noise, servo temperature, or battery power.
- The commanded speed proxy is stride/(cycle*duty), **not actual displacement**.
- The simulator foot error compares target kinematics with simulated actuator response; it is **not camera-observed foot tracking**.
- The support proxy counts stance feet within a 7 mm kinematic target tolerance; **it is not a force or stability measurement**.
- The fitness constraint of at most five proxy support-loss frames per test scenario and a 75% baseline-speed floor is an experimental choice, not a certified safety threshold.
- We intentionally never authorize live motor output. Hardware commissioning, contacts, terrain, torque and fall hazards remain untested.