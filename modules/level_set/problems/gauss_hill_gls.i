[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [./phi]
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
    type = GaussianHill
    center = '0.5 0.5 0.0'
  [../]
  [./velocity_front]
    type = ParsedVectorFunction
    value_y = 1
    value_x = 1
  [../]
[]

[Kernels]
  [./phi_advection]
    type = LevelSetAdvection
    variable = phi
    interface_velocity = velocity_front
  [../]
  [./phi_gls]
    type = LevelSetGLS
    variable = phi
    interface_velocity = velocity_front
  [../]
  [./phi_time]
    type = TimeDerivative
    variable = phi
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

[Preconditioning]
  [./fdp]
    type = FDP
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)
  type = Transient
  dt = 0.005
  l_max_its = 200
  nl_max_its = 100
  solve_type = PJFNK
  petsc_options_iname = -ksp_gmres_restart
  petsc_options_value = 500
  end_time = 1
  scheme = bdf2
  nl_abs_tol = 1e-9
  line_search = none
  l_tol = 1e-04
[]

[Adaptivity]
  max_h_level = 2
  initial_steps = 2
  marker = marker
  initial_marker = marker
  [./Indicators]
    [./indicator]
      type = GradientJumpIndicator
      variable = phi
    [../]
  [../]
  [./Markers]
    [./marker]
      type = ErrorFractionMarker
      coarsen = 0.15
      indicator = indicator
      refine = 0.7
    [../]
  [../]
[]

[Outputs]
  output_initial = true
  exodus = true
  [./console]
    type = Console
    perf_log = true
    linear_residuals = true
  [../]
[]

