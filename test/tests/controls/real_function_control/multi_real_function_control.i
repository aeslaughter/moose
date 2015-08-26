[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [./u]
  [../]
  [./v]
  [../]
[]

[Kernels]
  [./diff_u]
    type = CoefDiffusion
    variable = u
    coef = 0.1
  [../]
  [./time_u]
    type = TimeDerivative
    variable = u
  [../]
  [./diff_v]
    type = CoefDiffusion
    variable = v
    coef = 0.2
  [../]
  [./time_v]
    type = TimeDerivative
    variable = v
  [../]
[]

[BCs]
  [./left]
    type = DirichletBC
    variable = u
    boundary = left
    value = 0
  [../]
  [./right]
    type = DirichletBC
    variable = u
    boundary = right
    value = 1
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)
  type = Transient
  num_steps = 5
  dt = 0.1
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  csv = true
  output_initial = true
  print_linear_residuals = true
  print_perf_log = true
[]

[Functions]
  [./func_coef]
    type = ParsedFunction
    value = '2*t + 0.1'
  [../]
[]

[Postprocessors]
  [./u_coef]
    type = RealParameterReporter
    parameter = 'Kernels/diff_u/coef'
    execute_on = 'timestep_begin'
  [../]
  [./v_coef]
    type = RealParameterReporter
    parameter = 'Kernels/diff_v/coef'
    execute_on = 'timestep_begin'
  [../]
[]

[Controls]
  [./func_control]
    type = RealFunctionControl
    parameter = 'coef'
    function = 'func_coef'
    execute_on = 'timestep_begin'
  [../]
[]
