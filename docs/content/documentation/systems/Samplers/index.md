# Samplers System

The Sampler system provides different sampling strategies which can be use to perform sensitivity and
uncertainty analysis, probability risk analysis and data assimilation for MOOSE and MOOSE-based applications.
Input parameters will be perturbed using associated distributions from the Distribution System.

## Example Syntax
!listing modules/stochastic_tools/tests/samplers/monte_carlo/sampler_materials_test.i block=Samplers

!syntax parameters /Samplers

!syntax objects /Samplers

!syntax subsystems /Samplers

