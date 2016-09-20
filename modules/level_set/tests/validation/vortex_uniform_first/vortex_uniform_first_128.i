[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 128
  ny = 128
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
  [./inside]
    family = LAGRANGE
    order = FIRST
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
  [./inside]
    type = ThresholdAuxKernel
    threshold_variable = phi
    variable = inside
    above_value = 0
    below_value = 1
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
    value = 'sqrt((x-x0)*(x-x0) + (y-y0)*(y-y0)) - r'
    vars = 'x0 y0 r'
    vals = '0.5 0.75 0.15'
  [../]
  [./velocity_front_x]
    type = ParsedFunction
    value = 2*sin(2*pi*y)*sin(pi*x)*sin(pi*x)*cos(pi*t)
  [../]
  [./velocity_front_y]
    type = ParsedFunction
    value = -sin(2*pi*x)*sin(pi*y)*sin(pi*y)*cos(pi*t)
  [../]
[]

[Kernels]
  [./phi_advection]
    type = LevelSetAdvection
    variable = phi
    velocity_x = velocity_x
    velocity_y = velocity_y
  [../]
  [./phi_time]
    type = TimeDerivative
    variable = phi
  [../]
[]

[Postprocessors]
  [./area]
    type = ElementIntegralVariablePostprocessor
    variable = inside
    execute_on = 'initial timestep_end'
  [../]
  [./l2_error]
    type = ElementL2Error
    function = phi_initial
    variable = phi
    execute_on = 'initial timestep_end'
  [../]
  [./ndofs]
    type = NumDOFs
    execute_on = 'initial timestep_end'
  [../]
[]

[Preconditioning]
  [./smp]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_sub_type -ksp_gmres_restart'
    petsc_options_value = 'asm      ilu           300'
  [../]
[]

[Executioner]
  type = Transient
  dt = 0.001
  l_max_its = 100
  nl_max_its = 100
  solve_type = PJFNK
  end_time = 1
  nl_abs_tol = 1e-14
  scheme = 'implicit-euler'
[]

[Outputs]
  output_initial = true
  csv = true
  [./out]
    type = Exodus
    interval = 10
  [../]
  [./checkpoint]
    type = Checkpoint
    interval = 25
  [../]
  [./console]
    type = Console
    perf_log = true
    output_linear = true
  [../]
[]
