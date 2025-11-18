# QCDesigner 
This is an EDA software for superconducting quantum circuits. Having used it for years, I am now integrating its components to develop a tool that will free up human resources in circuit design and simulation.

## Update
* **20250912** Published V0.1.

## Layout design
The basic function is to write Python scripts to design GDS files. It is lightly dependent on the package GDSFactpry.

### 2D calculators 
Equations are valuable resources for making a design. 2D calculators use simplified models to generate a initial design that you can work on. 

### Auto-router
Not all parts of a chip need careful design. Just focusing on the important parts, and auto-router will do the rest.

## COMSOL simulation
We can directly call COMSOL for simulation via the package MPh.
