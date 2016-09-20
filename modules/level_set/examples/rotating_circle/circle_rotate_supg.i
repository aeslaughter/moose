[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = -1
  xmax = 1
  ymin = -1
  ymax = 1
  nx = 32
  ny = 32
#  elem_type = QUAD9
#  second_order = true
  uniform_refine = 2
[]
#
#[Adaptivity]
#  marker = marker
#  max_h_level = 2
#  [./Indicators]
#    [./grad_jump]
#      type = GradientJumpIndicator
#      variable = phi
#    [../]
#  [../]
#  [./Markers]
#    [./error_frac]
#      type = ErrorFractionMarker
#      indicator = grad_jump
#      coarsen = 0.1
#      refine = 0.9
#    [../]
#    [./interface]
#      type = ValueRangeMarker
#      variable = phi
#      lower_bound = 0.45
#      upper_bound = 0.55
#      buffer_size = 0.15
#      third_state = DONT_MARK
#    [../]
#    [./marker]
#      type = ComboMarker
#      markers = 'error_frac interface'
#    [../]
#  [../]
#[]

[AuxVariables]
  [./vel_x]
  [../]
  [./vel_y]
  [../]
[]

[AuxKernels]
  [./vel_x]
    type = FunctionAux
    function = 4*y
    variable = vel_x
    execute_on = initial
  [../]
  [./vel_y]
    type = FunctionAux
    function = -4*x
    variable = vel_y
    execute_on = initial
  [../]
[]

[Variables]
  [./phi]
  [../]
[]

[BCs]
  active = ''
  [./all]
    type = DirichletBC
    variable = phi
    boundary = 'top bottom left right'
    value = 0
  [../]
[]


[Functions]
  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.03
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

  [./advection_supg]
    type = LevelSetAdvectionSUPG
    velocity_x = vel_x
    velocity_y = vel_y
    variable = phi
  [../]

  [./time_supg]
    type = LevelSetTimeDerivativeSUPG
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
  solve_type = PJFNK
  start_time = 0
  end_time = 1.570796
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
