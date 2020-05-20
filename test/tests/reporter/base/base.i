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
  [b]
    type = TestGetReporter
    int_reporter = a::int
    real_reporter = a::real
    vector_reporter = a::vector
    string_reporter = a::string
  []
  [a]
    type = TestDeclareReporter
  []
[]

[Executioner]
  type = Steady
[]

[Outputs]
[]
