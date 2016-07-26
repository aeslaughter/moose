[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 2
  ny = 2
[]

[Variables]
  [./u]
    initial_condition = 2
  [../]
[]

[Postprocessors]
  [./l2_norm]
    type = SolutionL2Norm
  [../]
[]

[Problem]
  solve = false
[../]

[Executioner]
  type = Steady
  solve_type = 'PJFNK'
[]

[Outputs]
  execute_on = 'TIMESTEP_END'
  csv = true
[]
