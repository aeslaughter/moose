[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [./u]
  [../]
[]

[Kernels]
  [./diff]
    type = CoefDiffusion
    variable = u
    coef = 0.1
  [../]
  [./time]
    type = TimeDerivative
    variable = u
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

[Dampers]
  [./make_it_fail]
    type = ConstantDamper
    variable = u
    damping = 0.1
  [../]
[]

[Executioner]
  type = Transient
  num_steps = 20
  dt = 0.1
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  print_linear_residuals = false
  csv = true
[]

[Postprocessors]
  [./pp]
    type = PointValue
    variable = u
    point = '0.5 0.5 0'
  [../]
[]

[Controls]
  [./enable_damper]
    type = TimePeriod
    enable_objects = 'Damper::make_it_fail'
    start_time = 0.99
    end_time = 1.01
    execute_on = 'initial timestep_begin nonlinear' # execute on non-linear so the damping shuts off after the timestep is cut
  [../]
[]
