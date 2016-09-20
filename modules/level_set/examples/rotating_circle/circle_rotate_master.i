[Mesh]
  type = GeneratedMesh
  dim = 2
  xmin = -1
  xmax = 1
  ymin = -1
  ymax = 1
  nx = 32
  ny = 32
  #elem_type = QUAD9
  #second_order = true
  uniform_refine = 2
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

#  [./advection_supg]
#    type = LevelSetAdvectionSUPG
#    velocity_x = vel_x
#    velocity_y = vel_y
#    variable = phi
#  [../]
#
#  [./time_supg]
#    type = LevelSetTimeDerivativeSUPG
#    velocity_x = vel_x
#    velocity_y = vel_y
#    variable = phi
#  [../]

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

[MultiApps]
  [./reinit]
    type = LevelSetReinitializationMultiApp
    input_files = 'circle_rotate_sub.i'
    execute_on = 'timestep_end'
  [../]
[]

[Transfers]
#  [./marker_to_sub]
#    type = LevelSetMeshRefinementTransfer
#    multi_app = reinit
#    source_variable = marker
#    variable = marker
#  [../]

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
  #file_base = output/circle_rotate_master
  csv = true
  [./out]
    type = Exodus
    interval = 5
  [../]
[]
