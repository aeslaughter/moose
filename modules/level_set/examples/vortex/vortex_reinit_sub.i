[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 1
  ymax = 1
  nx = 32
  ny = 32
  uniform_refine = 2
#  elem_type = QUAD9
[]

[Variables]
  [./phi]
    family = LAGRANGE
#    order = SECOND
  [../]
[]

[AuxVariables]
  [./phi_0]
    family = LAGRANGE
#    order = SECOND
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
    epsilon = 0.03#0.01184
  [../]
[]

[Problem]
  type = LevelSetReinitializationProblem
[]

[UserObjects]
  [./arnold]
    type = LevelSetOlssonTerminator
    tol = 1
    min_steps = 3
  [../]
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  start_time = 0
  num_steps = 100
  nl_abs_tol = 1e-14
  scheme = crank-nicolson
  line_search = none
  petsc_options_iname = '-pc_type -pc_sub_type'
  petsc_options_value = 'asm      ilu'
  dt = 0.0007#3
  #[./TimeStepper]
  #  type = IterationAdaptiveDT
  #  optimal_iterations = 4
  #  growth_factor = 1.25
  #  dt = 0.001
  #[../]
[]

[Outputs]
#  exodus = true
[]
