[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 8
  ny = 8
  uniform_refine = 3
[]

[Variables]
  [./phi]
  [../]
[]

[AuxVariables]
  [./phi_0]
  [../]
  [./phi_exact]
  [../]
[]

[Functions]
  [./phi_initial]
    type = ParsedFunction
    type = LevelSetBubbleFunction
    epsilon = 0.055
    center = '0.5 0.5 0'
    radius = 0.15
  [../]

  [./phi_exact]
    type = LevelSetBubbleFunction
    epsilon = 0.05
    center = '0.5 0.5 0'
    radius = 0.15
  [../]
[]

[ICs]
  [./phi_ic]
    type = FunctionIC
    function = phi_initial
    variable = phi
  [../]
  [./phi_0_ic]
    type = FunctionIC
    function = phi_initial
    variable = phi_0
  [../]
  [./phi_exact_ic]
    type = FunctionIC
    function = phi_exact
    variable = phi_exact
  [../]
[]

[Kernels]
  [./time]
    type = TimeDerivative
    variable = phi
  [../]

  [./reinit]
    type = LevelSetOlssonReinitialization
    variable = phi
    phi_0 = phi_0
    epsilon = 0.05
  [../]
[]


[Postprocessors]
  [./error]
    type = ElementL2Error
    variable = phi
    function = phi_exact
    execute_on = 'initial timestep_end'
  [../]
  [./ndofs]
    type = NumDOFs
  [../]
[]


[VectorPostprocessors]
  [./line]
    type = LineValueSampler
    start_point = '0 0.5 0'
    end_point =  '1 0.5 0'
    variable = phi
    num_points = 100
    sort_by = x
    execute_on = 'initial timestep_end'
  [../]
[]

[Executioner]
  type = Transient
  nl_abs_tol = 1e-14
  trans_ss_check = true
  ss_norm_type = L1
  ss_check_tol = 0.015625
  solve_type = PJFNK
  num_steps = 20
  start_time = 0
  scheme = crank-nicolson
  dt = 0.05
  petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
  petsc_options_value = 'hypre    boomeramg    300'
[]

[Outputs]
  [./out]
    type = CSV
    file_base = output/olsson_2d_out
    time_data = true
  [../]
[]
