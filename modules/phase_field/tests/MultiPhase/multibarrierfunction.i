[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 50
  ny = 50
  nz = 0
  xmin = 0
  xmax = 20
  ymin = 0
  ymax = 20
  elem_type = QUAD4
[]

[AuxVariables]
  [./eta1]
    order = FIRST
    family = LAGRANGE
  [../]
  [./eta2]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[BCs]
  [./Periodic]
    [./All]
      auto_direction = 'x y'
    [../]
  [../]
[]

[Materials]
  [./multibarrier]
    type = MultiBarrierFunctionMaterial
    block = 0
    etas = 'eta1 eta2'
    function_name = g
    outputs = exodus
  [../]
[]

[Executioner]
  type = Steady
  solve_type = 'NEWTON'
[]

[Problem]
  solve = false
[]

[Outputs]
  exodus = true
[]
