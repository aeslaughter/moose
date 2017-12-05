# Test for Jacobian correctness check of non-ordinary state-based peridynamic formulation for mechanics problem

[GlobalParams]
  displacements = 'disp_x disp_y'
  bond_status = bond_status
  full_jacobian = true
[]

[Mesh]
  type = GeneratedMeshPD
  dim = 2
  horizon_number = 3
  nx = 4
[]

[Variables]
  [./disp_x]
  [../]
  [./disp_y]
  [../]
[]

[Modules]
  [./Peridynamics]
    [./Master]
      formulation = NonOrdinaryState
      stabilization = Force
    [../]
  [../]
[]

[Materials]
  [./elasticity_tensor]
    type = ComputeIsotropicElasticityTensor
    youngs_modulus = 2e5
    poissons_ratio = 0.0
  [../]
  [./strain]
    type = CorrespondenceFNOSPD
  [../]
  [./stress]
    type = ComputeLinearElasticStress
  [../]
[]

[Preconditioning]
  [./SMP]
    type = SMP
    full = true
    petsc_options_iname = '-ksp_type -pc_type -snes_type'
    petsc_options_value = 'bcgs bjacobi test'
  [../]
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
[]
