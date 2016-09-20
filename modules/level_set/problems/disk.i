[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 16
  ny = 16
[]

[Adaptivity]
  max_h_level = 3
  initial_steps = 5
  marker = ranger_marker
  initial_marker = ranger_marker
  [./Indicators]
    [./indicator]
      type = GradientJumpIndicator
      variable = phi
    [../]
  [../]
  [./Markers]
    [./jump_marker]
      type = ErrorFractionMarker
      coarsen = 0.1
      indicator = indicator
      refine = 0.85
    [../]
    [./range_marker]
      type = ValueRangeMarker
      upper_bound = 0.001
      lower_bound = -0.001
      third_state = DO_NOTHING
      variable = phi
      buffer_size = 0.003
    [../]
  [../]
[]

[Variables]
  [./phi]
  [../]
[]

[AuxVariables]
  [./velocity_x]
  [../]
  [./velocity_y]
  [../]
[../]

[AuxKernels]
  [./velocity_x_aux]
    type = FunctionAux
    variable = velocity_x
    function = velocity_front_x
    execute_on = 'initial timestep_begin'
  [../]
  [./velocity_y_aux]
    type = FunctionAux
    variable = velocity_y
    function = velocity_front_y
    execute_on = 'initial timestep_begin'
  [../]
[]

[ICs]
  [./phi_ic]
    function = phi_initial
    variable = phi
    type = FunctionIC
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
    value = -sin(pi*y)*sin(pi*y)*sin(2*pi*x)*cos(pi*t/T)
    vars = T
    vals = 10
  [../]
  [./velocity_front_y]
    type = ParsedFunction
    value = sin(pi*x)*sin(pi*x)*sin(2*pi*y)*cos(pi*t/T)
    vars = T
    vals = 10
  [../]
[]

[Kernels]
  active = 'phi_advection phi_time'
  [./phi_advection]
    type = LevelSetAdvection
    variable = phi
    velocity_x = v_x
    velocity_y = v_y
  [../]
  #[./phi_supg]
  #  type = LevelSetAdvectionSUPG
  #  variable = phi
  #  velocity_user_object = velocity_uo
  #[../]
  [./phi_time]
    type = TimeDerivative
    variable = phi
  [../]
[]

#[BCs]
#  [./Periodic]
#    [./all]
#      variable = phi
#      auto_direction = 'x y'
#    [../]
#  [../]
#[]

[Preconditioning]
  active = ''
  [./fdp]
    type = FDP
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)
  type = Transient
  dt = 0.01
  l_max_its = 200
  nl_max_its = 100
  solve_type = PJFNK
  petsc_options_iname = -ksp_gmres_restart
  petsc_options_value = 500
  end_time = 10
  scheme = bdf2
  nl_abs_tol = 1e-13
  line_search = none
  l_tol = 1e-6
[]


[Outputs]
  output_initial = true
  exodus = true
  [./console]
    type = Console
    perf_log = true
    output_linear = true
  [../]
[]
