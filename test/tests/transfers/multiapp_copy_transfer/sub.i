[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 20
  xmin = 0
  xmax = 2
  ymin = 0
  ymax = 6
  elem_type = QUAD8
[]

[Variables]
  [./u]
    initial_condition = 10
  [../]
[]

[Kernels]
  [./diff]
    type = Diffusion
    variable = u
  [../]
  [./time]
    type = TimeDerivative
    variable = u
  [../]
[]

[BCs]
  [./bottom]
    type = PostprocessorDirichletBC
    variable = u
    boundary = bottom
    postprocessor = reciever
  [../]
  [./top]
    type = NeumannBC
    variable = u
    boundary = top
    value = 1.2345
  [../]
[]

[Postprocessors]
  [./reciever]
    type = Receiver
    default = 10
  [../]
[]

[Executioner]
  type = Transient
  num_steps = 5
  dt = 0.1
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  execute_on = 'initial timestep_end'
  exodus = true
[]
