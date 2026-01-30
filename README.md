# QCDesigner 
This is an EDA software for superconducting quantum circuits.

## Update
* **20260131** Uploaded QCDComsol and QCDAds (not linked to QCDesigner).
* **20250912** Published V0.1.

## Layout design
The basic function is to write Python scripts to design GDS files. It is lightly dependent on the package GDSFactpry.

### 2D calculators 
Equations are valuable resources for making a design. 2D calculators use simplified models to generate a initial design that you can work on. 

### Auto-router
Not all parts of a chip need careful design. Just focusing on the important parts, and auto-router will do the rest.

## Simulation
The following software interfaces can be automatelly called for electromagnetic simulation:

### [QCDComsol](https://github.com/chenqmion/QCDComsol)
The default finite element method (FEM) engine for circuit-in-package simulation and 3D cavity design.

### [QCDAds](https://github.com/chenqmion/QCDAds)
The method of moments (Momentum) engine that for simulating linear-circuit spectrum.
