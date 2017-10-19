[Mesh]
  file = 2blk-conf.e

  [./MortarInterfaces]
    [./middle]
      master = 100
      slave = 101
      subdomain = 1000
    [../]
  [../]
[]

[Functions]
  [./exact_sln]
    type = ParsedFunction
    value = y
  [../]
  [./ffn]
    type = ParsedFunction
    value = 0
  [../]
[]

[Variables]
  [./u]
    order = FIRST
    family = LAGRANGE
    block = '1 2'
  [../]

  [./lm_u]
    order = FIRST
    family = LAGRANGE
    block = middle
  [../]

  [./v]
    order = FIRST
    family = LAGRANGE
    block = '1 2'
  [../]

  [./lm_v]
    order = FIRST
    family = LAGRANGE
    block = middle
  [../]

[]

[Kernels]
  [./diff_u]
    type = Diffusion
    variable = u
    block = '1 2'
  [../]
  [./ffn]
    type = BodyForce
    variable = u
    function = ffn
    block = '1 2'
  [../]
  [./diff_v]
    type = Diffusion
    variable = v
    block = '1 2'
  [../]
  [./coupled_u]
    type = CoupledForce
    variable = v
    v = u
    block = '1 2'
  [../]
[]

[Constraints]
  [./ced_u]
    type = EqualValueConstraint
    variable = lm_u
    interface = middle
    master_variable = u
  [../]
  [./ced_v]
    type = EqualValueConstraint
    variable = lm_v
    interface = middle
    master_variable = v
  [../]
[]

[BCs]
  [./all]
    type = FunctionDirichletBC
    variable = u
    boundary = '1 2 3 4'
    function = exact_sln
  [../]
  [./allv]
    type = DirichletBC
    variable = v
    boundary = '1 2 3 4'
    value = 0
  [../]
[]

[Postprocessors]
  [./l2_error]
    type = ElementL2Error
    variable = u
    function = exact_sln
    block = '1 2'
    execute_on = 'initial timestep_end'
  [../]
  [./l2_v]
    type = ElementL2Norm
    variable = v
    block = '1 2'
    execute_on = 'initial timestep_end'
  [../]
[]

[Preconditioning]
  [./fmp]
    type = SMP
    full = true
    solve_type = 'NEWTON'
  [../]
[]

[Executioner]
  type = Steady
  nl_rel_tol = 1e-12
  l_tol = 1e-12
[]

[Outputs]
  exodus = true
[]
