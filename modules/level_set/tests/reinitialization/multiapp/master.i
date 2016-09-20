[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = 0
  xmax = 1
  ymin = 0
  ymax = 1
  nx = 8
  ny = 8
  uniform_refine = 3 #1/64
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
  num_steps = 1000
  start_time = 0
  end_time = 4
  scheme = crank-nicolson
  petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
  petsc_options_value = 'hypre    boomeramg    100'

  [./TimeStepper]
    type = PostprocessorDT
    postprocessor = cfl
    scale = 0.8
  [../]

[]

[MultiApps]
  [./reinit]
    type = LevelSetReinitializationMultiApp
    input_files = 'reinit.i'
    execute_on = 'timestep_end'
  [../]
[]

[Transfers]
  #active = 'to_sub to_sub_init'
  [./to_sub]
    type = LevelSetSolutionTransfer
    from_variable = phi
    to_variable = phi
    direction = to_multiapp
    multi_app = reinit
    execute_on = 'timestep_end'
  [../]

  [./to_sub_init]
    type = LevelSetSolutionTransfer
    from_variable = phi
    to_variable = phi_0
    direction = to_multiapp
    multi_app = reinit
    execute_on = 'timestep_end'
  [../]

  [./from_sub]
    type = LevelSetSolutionTransfer
    from_variable = phi
    to_variable = phi
    direction = from_multiapp
    multi_app = reinit
    execute_on = timestep_end
  [../]
[]

[Outputs]
  intervel = 4
  exodus = true
  csv = true
[]
