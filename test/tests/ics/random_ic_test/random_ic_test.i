[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 50
  ny = 50

  nz = 0
  zmax = 0
[]

[Variables]
  active = 'u'

  [./u]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[ICs]
  [./u_ic]
    type = RandomIC
    variable = u
  [../]

  [./u_aux_ic]
    type = RandomIC
    seed = 5
    variable = u_aux
  [../]
[]

[AuxVariables]
  active = 'u_aux'

  [./u_aux]
    order = FIRST
    family = LAGRANGE
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
    boundary = 3
    value = 0
  [../]

  [./right]
    type = DirichletBC
    variable = u
    boundary = 1
    value = 1
  [../]
[]

[Executioner]
  type = Steady

  # Preconditioned JFNK (default)
  solve_type = 'PJFNK'
  nl_rel_tol = 1e-10
[]

[Outputs]
  file_base = out
  exodus = true
[]
