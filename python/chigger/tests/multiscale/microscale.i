[Problem]
  coord_type = 'RSPHERICAL'
[]

[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 20
  xmin = 0
  xmax = 0.1
[]

[Variables]
  [./T]
  [../]
[]

[AuxVariables]
  [./energy_per_volume_fuel_matrix]
    initial_condition = 5e5
  [../]
[]

[Kernels]
  [./diffusion]
    type = HeatConduction
    variable = T
    diffusion_coefficient = 'k_s'
  [../]
  [./heat_source]
    type = CoupledForce
    variable = T
    v = energy_per_volume_fuel_matrix
  [../]
[]

[Materials]
  [./properties]
    type = GenericConstantMaterial
    prop_names = 'k_s'
    prop_values = 2.0
  [../]
[../]

[BCs]
  [./right]
    type = DirichletBC
    variable = T
    value = 0.0
    boundary = 'right'
  [../]
[]

[Executioner]
  type = Transient
  num_steps = 2
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
  solve_type = PJFNK
  nl_abs_tol = 1e-6
[]

[Preconditioning]
  [./SMP_Newton]
    type = SMP
    full = true
    solve_type = 'PJFNK'
    petsc_options = '-snes_ksp_ew'
    petsc_options_iname = '-pc_type' #-pc_factor_mat_solver_package'
    petsc_options_value = ' lu     ' # mumps                       '
  [../]
[]

[Outputs]
  exodus = true
  print_linear_residuals = false
[]
