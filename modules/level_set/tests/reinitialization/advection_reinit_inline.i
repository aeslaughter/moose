[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = 0
  xmax = 1
  ymin = 0
  ymax = 1
  nx = 8
  ny = 8
  uniform_refine = 3
[]

[AuxVariables]
  [./vel_x]
    initial_condition = 1
  [../]
  [./vel_y]
    initial_condition = 1
  [../]
[]

[Variables]
  [./phi]
  [../]
[]

[Functions]
  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.05
    center = '0.5 0.5 0'
    radius = 0.15
  [../]
[]

[BCs]
  [./Periodic]
    [./all]
      variable = phi
      auto_direction = 'x y'
    [../]
  [../]
[]

[ICs]
  [./phi_ic]
    type = FunctionIC
    function = phi_exact
    variable = phi
  [../]
[]

[Kernels]
  [./time]
    type = TimeDerivative
    variable = phi
  [../]

  [./advection]
    type = LevelSetAdvection
    velocity_x = vel_x
    velocity_y = vel_y
    variable = phi
  [../]


  [./olsson]
    type = LevelSetOlssonReinitialization
    variable = phi
    epsilon = 0.05
    phi_0 = phi
    mu = 1
  [../]
[]

[Postprocessors]
  [./area]
    type = LevelSetVolume
    threshold = 0.5
    variable = phi
    location = outside
    execute_on = 'initial timestep_end'
  [../]
  [./cfl]
    type = CFLCondition
    velocity_x = vel_x
    velocity_y = vel_y
    execute_on = 'initial' #timestep_end'
  [../]
[]

[Executioner]
  type = Transient
  l_max_its = 40
  nl_max_its = 10
  solve_type = PJFNK
  start_time = 0
  end_time = 4
  scheme = crank-nicolson
  petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
  petsc_options_value = 'hypre    boomeramg    100'


  [./TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.001
    optimal_iterations = 5
    iteration_window = 1
  #  type = PostprocessorDT
  #  postprocessor = cfl
  #  scale = 0.1
  [../]
[]

[Outputs]
  csv = true
  exodus = true
[]
