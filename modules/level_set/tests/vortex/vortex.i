[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 64
  ny = 64
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

[Modules]
  [./LevelSet]
    variable = phi
    velocity_x = velocity_x
    velocity_y = velocity_y
    cfl = 'cfl'
    volume = 'area'
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
  l_max_its = 100
  nl_max_its = 100
  solve_type = PJFNK
  start_time = 0
  end_time = 1
  nl_abs_tol = 1e-15
  nl_rel_tol = 1e-13
  scheme = crank-nicolson
  [./TimeStepper]
    type = PostprocessorDT
    postprocessor = cfl
    scale = 0.7
  [../]
[]

[Outputs]
  [./out]
    type = CSV
    interval = 10
    execute_on = 'initial timestep_end final'
  [../]
  [./exodus]
    type = Exodus
    interval = 10
    execute_on = 'initial timestep_end'
  [../]
[]
