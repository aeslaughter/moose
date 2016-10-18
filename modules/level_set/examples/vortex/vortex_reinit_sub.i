[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 32
  ny = 32
  uniform_refine = 2
  elem_type = TRI6
  second_order = true

[]

[Variables]
  [./phi]
    family = LAGRANGE
  [../]
[]

[AuxVariables]
  [./phi_0]
    family = LAGRANGE
  [../]
  [./marker]
    family = MONOMIAL
    order = CONSTANT
  [../]
[]

[Kernels]
  [./time]
    type = TimeDerivative
    variable = phi
  [../]

  [./reinit]
    type = LevelSetOlssonReinitialization
    variable = phi
    phi_0 = phi_0
    epsilon = 0.03
  [../]
[]

[Problem]
  type = LevelSetReinitializationProblem
[]

[UserObjects]
  [./arnold]
    type = LevelSetOlssonTerminator
    tol = 0.5
    min_steps = 5
  [../]
[]

[Executioner]
  type = Transient
  solve_type = PJFNK
  start_time = 0
  num_steps = 100
  nl_rel_tol = 1e-8
 # nl_abs_tol = 1e-12
  scheme = crank-nicolson
  line_search = none
  petsc_options_iname = '-pc_type -pc_sub_type'
  petsc_options_value = 'hypre     boomeramg'
  dt = 0.01
[]

[Outputs]
#  exodus = true
[]
