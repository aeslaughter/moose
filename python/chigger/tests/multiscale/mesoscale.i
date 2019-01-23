[Mesh]
  type = GeneratedMesh
  dim = 3
  xmin = -1
  xmax =  1
  ymin = -1
  ymax =  1
  zmin = -1
  zmax =  1
  nx = 8
  ny = 8
  nz = 8
[]

[Variables]
  [./T]
  [../]
[]

[AuxVariables]
  [./energy_per_volume_fuel_matrix]
    initial_condition = 1e2
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
  [./solid_properties]
    type = GenericConstantMaterial
    prop_names = 'k_s'
    prop_values = '0.5'
  [../]
[]

[BCs]
  [./left]
    type = DirichletBC
    variable = T
    value = 1100
    boundary = 'left'
  [../]
  [./right]
    type = DirichletBC
    variable = T
    value = 1200
    boundary = 'right'
  [../]
[]

[MultiApps]
  [./particles]
    type = TransientMultiApp
    positions = '0.1 0.2 0.3
                -0.5 0.0 0.0'
    execute_on = 'TIMESTEP_END'
    input_files = 'microscale.i'
    output_in_position = true
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
