[Mesh]
  file = square.e
[]

[Variables]
  active = 'u'

  [./u]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[AuxVariables]
  active = 'u_aux'

  [./u_aux]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[ICs]
  [./u_ic]
    type = FunctionIC
    function = initial_cond_func
    variable = u
  [../]
  [./u_aux_ic]
    type = FunctionIC
    function = initial_cond_func
    variable = u_aux
  [../]
[]

[Functions]
  [./initial_cond_func]
    type = ParsedFunction
    value = x+2
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
