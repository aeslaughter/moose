[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = 12
  nx = 24
[]

[Adaptivity]
  steps = 5
  marker = marker
  [./Markers]
    [./marker]
      type = UniformMarker
      mark = REFINE
    [../]
  [../]
[]

[Variables]
  [./phi]
  [../]
[]

[AuxVariables]
  [./v_x]
  [../]
[]

[AuxKernels]
  [./velocity_x_aux]
    type = FunctionAux
    variable = v_x
    function = 'cos(pi*x)'
    execute_on = initial
  [../]
[]

[BCs]
  [./all]
    type = FunctionDirichletBC
    boundary = 'right'
    function = phi_exact
    variable = phi
  [../]
[]

[Functions]
  [./phi_exact]
    type = ParsedFunction
    value = 'a*sin(pi*x/b)*cos(pi*x)'
    vars = 'a b'
    vals = '2 12'
  [../]
  [./phi_mms]
    type = ParsedFunction
    value = '(-pi*a*sin(pi*x)*sin(pi*x/b) + pi*a*cos(pi*x)*cos(pi*x/b)/b)*cos(pi*x)'
    vars = 'a b'
    vals = '2 12'
  [../]
[]

[Kernels]
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
  [./phi_sample]
    type = LineValueSampler
    num_points = 5000
    start_point = '0 0 0'
    end_point = '12 0 0'
    sort_by = 'x'
    variable = phi
  [../]
[]

[Executioner]
  type = Steady
  petsc_options_iname = '-pc_type -pc_sub_type'
  petsc_options_value = 'asm      ilu'
[]

[Outputs]
  execute_on = 'TIMESTEP_END'
  csv = true
[]
