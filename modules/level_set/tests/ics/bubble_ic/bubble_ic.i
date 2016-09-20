[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 32
  ny = 32
  uniform_refine = 2
[]

[Variables]
  [./phi]
  [../]
[]

[ICs]
  [./phi_ic]
    type = LevelSetBubbleIC
    center = '0.5 0.5 0'
    radius = 0.15
    epsilon = 0.02
    variable = phi
  [../]
[]

[Problem]
  solve = false
[]

[Executioner]
  type = Steady
[]

[Outputs]
  execute_on = initial
  exodus = true
[]
