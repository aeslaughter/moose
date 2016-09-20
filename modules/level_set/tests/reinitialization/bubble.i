[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = -1
  xmax = 1
  ymin = -1
  ymax = 1
  nx = 8
  ny = 8
[]

[AuxVariables]
  [./vel_x]
  [../]
  [./vel_y]
  [../]
[]

[AuxKernels]
  [./vel_x_func]
    type = FunctionAux
    variable = vel_x
    function = '-4*y'
  [../]
  [./vel_y_func]
    type = FunctionAux
    variable = vel_y
    function = '4*x'
  [../]
[]

[Variables]
  [./phi]
  [../]
[]

[Functions]
  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.03125
    center = '0 0.5 0'
    radius = 0.15
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

  [./supg]
    type = LevelSetSUPG
    velocity_x = vel_x
    velocity_y = vel_y
    variable = phi
  [../]

  [./reinit]
    type = LevelSetOlssonReinitialization
    variable = phi
    phi_0 = phi
    epsilon = 0.03125
    mu = 0.5
  [../]
[]

[Postprocessors]
  [./area]
    type = LevelSetVolume
    threshold = 0.5
    variable = phi
    execute_on = 'initial timestep_end'
  [../]

[]

[Preconditioning]
  type = FDP
  [./fdp]
    type = FDP
  [../]

[Executioner]
  type = Transient
  l_max_its = 40
  nl_max_its = 10
  solve_type = PJFNK
  num_steps = 1000
  start_time = 0
  end_time = 1.57079632679
  #end_time = 6.28318530718
  #nl_abs_tol = 1e-13
  scheme = crank-nicolson
  petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
  petsc_options_value = 'hypre    boomeramg    100'
  dt = 0.005
  [./TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.001
    growth_factor = 1.1
    cutback_factor = 0.9
    optimal_iterations = 5
  [../]
[]

[Adaptivity]
  marker = marker
  max_h_level = 6
  initial_marker = marker
  initial_steps = 6
  [./Markers]
    [./marker]
      type = ValueRangeMarker
      variable = phi
      lower_bound = 0.2
      upper_bound = 0.8
    [../]
  [../]
[]

[Outputs]
  csv = true
  [./out]
    type = Exodus
    interval = 10
  [../]
[]
