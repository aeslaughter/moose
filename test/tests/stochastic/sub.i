[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
  xmax = 0.1
  ymax = 0.1
  uniform_refine = 2
[]

[Variables]
  [./u]
  [../]
[]

[Kernels]
  [./diff]
    type = MatDiffusion
    prop_name = 'conductivity'
    variable = u
  [../]
[]

[BCs]
  [./left]
    type = FunctionDirichletBC
    function = '3*sin(pi*y)'
    variable = u
    boundary = left
  [../]
  [./right]
    type = FunctionNeumannBC
    variable = u
    boundary = right
    function = '5*cos(pi*y)'
  [../]
[]

[Functions]
  [./cond_func]
    type = ParsedFunction
    value = 'cond'
    vars = 'cond'
    vals = 'conductivity'
  [../]
[]

[Materials]
  [./mat]
    type = GenericFunctionMaterial
    prop_names = 'conductivity'
    prop_values = 'cond_func'
  [../]
[]

[Executioner]
  type = Steady
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Postprocessors]
  [./side_average]
    type = SideAverageValue
    boundary = right
    variable = u
  [../]
  [./conductivity]
    type = Receiver
    default = 3
  [../]
[]

[Outputs]
[]
