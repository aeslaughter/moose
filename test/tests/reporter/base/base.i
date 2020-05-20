[Mesh]
  type = GeneratedMesh
  dim = 1
[]

[Variables/u]
[]

[Problem]
  solve = false
  kernel_coverage_check = false
[]

[Reporters]
  [a]
    type = TestDeclareReporter
  []
  [b]
    type = TestGetReporter
    reporter = a::value
  []
[]

[Executioner]
  type = Steady
[]

[Outputs]
[]
