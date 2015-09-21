[Mesh]
  active = ''
  file = square.e
  uniform_refine = 3

  [./inactive]
    type = NonexistentAction
  [../]
[]

[Variables]
  active = 'u'

  [./u]
    order = FIRST
    family = LAGRANGE
  [../]

  [./u_aux]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[ICs]
  [./u_ic]
    type = BoundingBoxIC
    x1 = 0.1
    y1 = 0.1
    x2 = 0.6
    y2 = 0.6
    inside = 2.3
    outside = 4.6
    variable = u
  [../]
  [./u_aux]
    type = BoundingBoxIC
    x1 = 0.1
    y1 = 0.1
    x2 = 0.6
    y2 = 0.6
    inside = 1.34
    outside = 6.67
    variable = u_aux
  [../]
[]

[AuxVariables]
  active = 'u_aux'

  [./u_aux]
    order = FIRST
    family = LAGRANGE
    [../]
  [../]
[]

[Kernels]
  active = 'diff'

  [./diff]
    type = Diffusion
    variable = u
  [../]
[]

[BCs]
  active = 'left right'

  [./left]
    type = DirichletBC
    variable = u
    boundary = 1
    value = 0
  [../]

  [./right]
    type = DirichletBC
    variable = u
    boundary = 2
    value = 1
  [../]

  [./inactive]
    type = NonexistentBC
  [../]
[]

[Executioner]
  type = Steady

  # Preconditioned JFNK (default)
  solve_type = 'PJFNK'
[]

[Outputs]
  file_base = out
  exodus = true
[]
