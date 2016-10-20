[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = 32
  nx = 64
[]

[Variables]
  [./phi]
  [../]
[]

[AuxVariables]
  [./v_x]
    initial_condition = 2
  [../]
[]

[BCs]
  [./left]
    type = FunctionDirichletBC
    boundary = 'left'
    function = phi_exact
    variable = phi
  [../]
[]

[Functions]
  [./phi_exact]
    type = ParsedFunction
    value = 'a*exp(1/(10*t))*sin(2*pi*x/b) + 1'
    vars = 'a b'
    vals = '1 8'
  [../]
  [./phi_mms]
    type = ParsedFunction
    value = '-a*exp(1/(10*t))*sin(2*pi*x/b)/(10*t^2) + 2*pi*a*exp(1/(10*t))*cos(2*pi*x/b)/b'
    vars = 'a b'
    vals = '1 8'
  [../]
[]

[Kernels]
  [./time]
    type = TimeDerivative
    variable = phi
  [../]
  [./time_supg]
    type = LevelSetTimeDerivativeSUPG
    variable = phi
    velocity_x = v_x
  [../]
  [./phi_advection]
    type = LevelSetAdvection
    variable = phi
    velocity_x = v_x
  [../]
  [./phi_forcing]
    type = UserForcingFunction
    variable = phi
    function = phi_mms
  [../]
  [./phi_advection_supg]
    type = LevelSetAdvectionSUPG
    variable = phi
    velocity_x = v_x
  [../]
  [./phi_forcing_supg]
    type = LevelSetForcingFunctionSUPG
    velocity_x = v_x
    variable = phi
    function = phi_mms
  [../]
[]

[Postprocessors]
  [./error]
    type = ElementL2Error
    function = phi_exact
    variable = phi
  [../]
  [./h]
    type = AverageElementSize
    variable = phi
  [../]
[]

[VectorPostprocessors]
  active = ''
  [./results]
    type = LineValueSampler
    variable = phi
    start_point = '0 0 0'
    end_point = '12 0 0'
    num_points = 500
    sort_by = x
  [../]
[]

[Executioner]
  type = Transient
  start_time = 1
  dt = 0.01
  end_time = 1.25
  nl_rel_tol = 1e-10
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu       superlu_dist'
[]

[Outputs]
  execute_on = 'TIMESTEP_END'
  csv = true
[]
