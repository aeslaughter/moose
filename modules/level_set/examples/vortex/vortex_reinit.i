[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 32
  ny = 32
  uniform_refine = 2
  elem_type = TRI6
  second_order = true
[]

#[Adaptivity]
#  marker = marker
#  max_h_level = 3
#  [./Markers]
#    [./marker]
#      type = ValueRangeMarker
#      variable = phi
#      lower_bound = 0.3
#      upper_bound = 0.7
#      buffer_size = 0.2
#      third_state = DONT_MARK
#    [../]
#  [../]
#[]

[AuxVariables]
  [./vel_x]
    family = LAGRANGE
  [../]
  [./vel_y]
    family = LAGRANGE
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
    type = LevelSetOlssonVortex
    component = x
    reverse_time = 1
  [../]
  [./vel_y]
    type = LevelSetOlssonVortex
    component = y
    reverse_time = 1
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
  active = 'time advection'
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
  [./time_supg]
    type = LevelSetTimeDerivativeSUPG
    variable = phi
    velocity_x = vel_x
    velocity_y = vel_y
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

[Problem]
  type = LevelSetProblem
[]

[Executioner]
  type = Transient
  solve_type = PJFNK
  start_time = 0
  end_time = 1
  scheme = crank-nicolson
  petsc_options_iname = '-pc_type -pc_sub_type'
  petsc_options_value = 'asm      ilu'
  [./TimeStepper]
    type = PostprocessorDT
    postprocessor = cfl
    scale = 0.3
  [../]
[]

[MultiApps]
  [./reinit]
    type = LevelSetReinitializationMultiApp
    input_files = 'vortex_reinit_sub.i'
    execute_on = TIMESTEP_END
  [../]
[]

[Transfers]
  [./marker_to_sub]
    type = LevelSetMeshRefinementTransfer
    multi_app = reinit
    source_variable = marker
    variable = marker
  [../]

  [./to_sub]
    type = MultiAppCopyTransfer
    source_variable = phi
    variable = phi
    direction = to_multiapp
    multi_app = reinit
    execute_on = 'timestep_end'
  [../]

  [./to_sub_init]
    type = MultiAppCopyTransfer
    source_variable = phi
    variable = phi_0
    direction = to_multiapp
    multi_app = reinit
    execute_on = 'timestep_end'
  [../]

  [./from_sub]
    type = MultiAppCopyTransfer
    source_variable = phi
    variable = phi
    direction = from_multiapp
    multi_app = reinit
    execute_on = 'timestep_end'
  [../]
[]

[Outputs]
  csv = true
  [./out]
    file_base = output/vortex_reinit_out
    type = Exodus
    interval = 5
    execute_on = 'initial timestep_end final'
  [../]
[]
