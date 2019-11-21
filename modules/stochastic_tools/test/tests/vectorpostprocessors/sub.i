[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [u]
  []
[]

[Kernels]
  [diff]
    type = ADDiffusion
    variable = u
  []
  [time]
    type = ADTimeDerivative
    variable = u
  []
[]

[BCs]
  [left]
    type = DirichletBC
    variable = u
    boundary = left
    value = 0
  []
  [right]
    type = NeumannBC
    variable = u
    boundary = right
    value = 100
  []
[]

[Executioner]
  type = Transient
  num_steps = 5
  dt = 0.1
  solve_type = NEWTON
[]

[Postprocessors]
  [avg_temp_out]
    type = SideAverageValue
    variable = u
    boundary = right
  []
[]

[Controls]
  [stochastic]
    type = SamplerReceiver
  []
[]

[Outputs]
[]
