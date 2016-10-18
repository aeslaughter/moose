[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 16
  ny = 16
  uniform_refine = 4
  elem_type = QUAD9
[]

[Adaptivity]
  marker = marker
  max_h_level = 4
  [./Markers]
    [./marker]
      type = ValueRangeMarker
      variable = phi
      lower_bound = 0.47
      upper_bound = 0.53
      buffer_size = 0.24
      third_state = DO_NOTHING
    [../]
  [../]
[]

[AuxVariables]
  [./vel_x]
    family = LAGRANGE
    order = SECOND
  [../]
  [./vel_y]
    family = LAGRANGE
    order = SECOND
  [../]
[]

[AuxKernels]
  [./vel_x]
    type = FunctionAux
    function = vel_x
    variable = vel_x
    execute_on = 'initial timestep_begin'
  [../]
  [./vel_y]
    type = FunctionAux
    function = vel_y
    variable = vel_y
    execute_on = 'initial timestep_begin'
  [../]
[]

[Variables]
  [./phi]
    family = LAGRANGE
    order = SECOND
  [../]
[]

[Functions]
  [./phi_exact]
    type = LevelSetOlssonBubbleFunction
    epsilon = 0.03
    center = '0.5 0.75 0'
    radius = 0.15
  [../]
  [./vel_x]
    type = LevelSetVortex
    component = x
    reverse_time = 2
  [../]
  [./vel_y]
    type = LevelSetVortex
    component = y
    reverse_time = 2
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
 # active = 'time advection'
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
    type = LevelSetAdvectionSUPG
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
    type = LevelSetCFLCondition
    velocity_x = vel_x
    velocity_y = vel_y
    execute_on = 'initial timestep_end'
  [../]
[]

[Executioner]
  type = Transient
  solve_type = PJFNK
  start_time = 0
  end_time = 2
  scheme = crank-nicolson
  petsc_options_iname = '-pc_type -pc_sub_type'
  petsc_options_value = 'asm      ilu'
  [./TimeStepper]
    type = PostprocessorDT
    postprocessor = cfl
    scale = 0.8
  [../]
[]

[Outputs]
  file_base = output/vortex_supg_out
  csv = true
  [./out]
    type = Exodus
    interval = 5
    execute_on = 'initial timestep_end final'
  [../]
[]
