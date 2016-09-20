[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 16
  ny = 16
  #elem_type = QUAD9
[]

[Adaptivity]
  max_h_level = 6
  initial_steps = 6
  cycles_per_step = 5
  marker = ls_range_marker
  initial_marker = ls_range_marker
  [./Indicators]
    active = ''
    [./grad_jump]
      type = GradientJumpIndicator
      variable = phi
    [../]
    [./velocity_jump_x]
      type = GradientJumpIndicator
      variable = velocity_x
    [../]
    [./velocity_jump_y]
      type = GradientJumpIndicator
      variable = velocity_y
    [../]
  [../]
  [./Markers]
    active = 'range_marker ls_range_marker'
    [./jump_marker]
      type = ErrorFractionMarker
      coarsen = 0.2
      indicator = grad_jump
      refine = 0.7
    [../]
    [./ls_range_marker]
      type = LevelSetValueMarker
      upper_bound = 0.004
      lower_bound = -0.004
      min_lower_bound = -0.004
      min_upper_bound = 0.004
      third_state = DO_NOTHING
      variable = phi
      buffer_size = 0.01
      velocity_x = velocity_x
      velocity_y = velocity_y
      leading_scale = 2.5
      trailing_scale = 0.5
      scale_with_velocity = false
    [../]
    [./range_marker]
      type = ValueRangeMarker
      upper_bound = 0.005
      lower_bound = -0.005
      third_state = DO_NOTHING
      variable = phi
      buffer_size = 0.01
    [../]
  [../]
[]

[Variables]
  [./phi]
    #order = SECOND
  [../]
[]

[AuxVariables]
  [./velocity_x]
  [../]
  [./velocity_y]
  [../]
[]

[AuxKernels]
  [./velocity_x_aux]
    type = FunctionAux
    variable = velocity_x
    function = velocity_front_x
    execute_on = 'initial timestep_end'
  [../]
  [./velocity_y_aux]
    type = FunctionAux
    variable = velocity_y
    function = velocity_front_y
    execute_on = 'initial timestep_end'
  [../]
[]

[ICs]
  [./phi_ic]
    type = FunctionIC
    function = phi_initial
    variable = phi
  [../]

  [./velocity_x_ic]
    type = FunctionIC
    function = velocity_front_x
    variable = velocity_x
  [../]

  [./velocity_y_ic]
    type = FunctionIC
    function = velocity_front_y
    variable = velocity_y
  [../]

[]

[Functions]
  [./phi_initial]
    type = ParsedFunction
    value = '(x-x0)*(x-x0) + (y-y0)*(y-y0) - r*r'
    vars = 'x0 y0 r'
    vals = '0.5 0.75 0.15'
  [../]

  [./velocity_front_x]
    type = ParsedFunction
    value = sin(pi*x)*sin(pi*x)*sin(2*pi*y)*cos(pi*t/T)
    vars = T
    vals = 8
  [../]

  [./velocity_front_y]
    type = ParsedFunction
    value = -sin(pi*y)*sin(pi*y)*sin(2*pi*x)*cos(pi*t/T)
    vars = T
    vals = 8
  [../]

[]

[Kernels]
  #active = 'phi_time phi_advection'
  [./phi_advection]
    type = LevelSetAdvection
    variable = phi
    velocity_x = velocity_x
    velocity_y = velocity_y
  [../]
  [./phi_supg]
    type = LevelSetSUPG
    variable = phi
    velocity_x = velocity_x
    velocity_y = velocity_y
  [../]
  [./phi_time]
    type = TimeDerivative
    variable = phi
  [../]
[]

[Preconditioning]
  active = 'smp'
  [./fdp]
    type = FDP
  [../]
  [./smp]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
    petsc_options_value = 'asm      ilu           300'
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)

#  petsc_options_iname = '-pc_type'
#  petsc_options_value = 'lu'

#  petsc_options_iname = '-pc_type -pc_hypre_type -ksp_gmres_restart'
#  petsc_options_value = 'hypre boomeramg 500'
  # petsc_options_iname = -ksp_gmres_restart
  # petsc_options_value = 500
  type = Transient
  dt = 0.001
  l_max_its = 100
  nl_max_its = 100
  solve_type = PJFNK
#   solve_type = NEWTON
  end_time = 8
  #scheme = crank-nicolson
#  nl_abs_tol = 1e-10
#  line_search = none
#  nl_rel_tol = 1e-8
#  l_tol = 1e-4


  [./TimeStepper]
    type = PostprocessorDT
    dt = 0.001
    postprocessor = cfl
    #type = IterationAdaptiveDT
    #dt = 0.01
    #growth_factor = 1.15
  [../]
[]

[Postprocessors]
  [./cfl]
    type = CFLCondition
    velocity_x = velocity_x
    velocity_y = velocity_y
    coefficient = 0.3
    interface_width = interface_width
    execute_on = 'initial timestep_begin'
  [../]
  [./interface_width]
    type = InterfaceWidth
    execute_on = initial
    level = 1
  [../]
  [./num_elems]
    type = NumElems
  [../]
[]

[Outputs]
  output_initial = true
  interval = 1
  exodus = true
  checkpoint = true
  [./console]
    type = Console
    perf_log = true
    output_linear = true
    interval = 1
  [../]
[]
