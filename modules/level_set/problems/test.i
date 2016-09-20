[Mesh]
  # elem_type = QUAD9
  type = GeneratedMesh
  dim = 2
  nx = 256
  ny = 256
[]

[Variables]
  [./phi]
    # order = SECOND
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
  [./outside]
    family = LAGRANGE
    order = FIRST
  [../]
  [./grad_phi_x]
  [../]
  [./grad_phi_y]
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
    variable = inside
    above_value = 0
    below_value = 1
    execute_on = 'initial timestep_end'
    threshold_variable = phi
  [../]
  [./outside]
    type = ThresholdAuxKernel
    variable = outside
    execute_on = 'initial timestep_end'
    threshold_variable = phi
  [../]
  [./grad_phi_x]
    type = VariableGradientComponent
    variable = phi
    component = 0
  [../]
  [./grad_phi_y]
    type = VariableGradientComponent
    variable = phi
    component = 1
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

[Postprocessors]
  [./levelset_area]
    type = LevelSetVolume
    variable = phi
    execute_on = 'initial timestep_end'
  [../]
  [./total_araa]
    type = VolumePostprocessor
    execute_on = 'initial timestep_end'
  [../]
  [./inside_area]
    type = ElementIntegralVariablePostprocessor
    variable = inside
    execute_on = 'initial timestep_end'
  [../]
  [./outside_area]
    type = ElementIntegralVariablePostprocessor
    variable = outside
    execute_on = 'initial timestep_end'
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
  [./TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.001
  [../]
  type = Transient
  l_max_its = 100
  nl_max_its = 100
  solve_type = PJFNK
  end_time = 1
  nl_abs_tol = 1e-14
  scheme = implicit-euler
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
