[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 16
  ny = 16
  uniform_refine = 3
#  elem_type = QUAD9
[]

#[Adaptivity]
#  marker = marker
#  max_h_level = 3
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
#    order = SECOND
  [../]
  [./vel_y]
    family = LAGRANGE
#    order = SECOND
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
    #order = SECOND
  [../]
[]

[Functions]
  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.03#0.01184
    center = '0.5 0.75 0'
    radius = 0.15
  [../]
  [./vel_x]
    type = LevelSetVortex
    component = x
    reverse_time = 4
  [../]
  [./vel_y]
    type = LevelSetVortex
    component = y
    reverse_time = 4
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

[Problem]
  type = LevelSetProblem
[]

[Executioner]
  type = Transient
  solve_type = PJFNK
  #num_steps = 1
  start_time = 0
  end_time = 4
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
  #[./marker_to_sub]
  #  type = LevelSetMeshRefinementTransfer
  #  multi_app = reinit
  #  source_variable = marker
  #  variable = marker
  #[../]

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
    type = Exodus
    interval = 1
  #  execute_on = 'INITIAL TIMESTEP_BEGIN TIMESTEP_END'
  [../]
[]
