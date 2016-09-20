[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 32
  ny = 32
  uniform_refine = 1
  #elem_type = QUAD9
[]

#[Adaptivity]
#  marker = marker
#  max_h_level = 2
#  [./Markers]
#    [./marker]
#      type = ValueRangeMarker
#      variable = phi
#      lower_bound = 0.47
#      upper_bound = 0.53
#      buffer_size = 0.12
#      third_state = DO_NOTHING
#    [../]
#  [../]
#[]

[AuxVariables]
  [./vel_x]
    family = LAGRANGE
    order = FIRST
  [../]
  [./vel_y]
    family = LAGRANGE
    order = FIRST
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
    order = FIRST
  [../]
[]

[Functions]
  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.01184
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
  csv = true
  [./out]
    type = Exodus
    interval = 5
  [../]
[]
