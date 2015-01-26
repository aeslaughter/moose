[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [./u]
  [../]
[]

[Materials]
  [./stateful_tensor]
    type = TestStatefulTensor
    block = 0
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
  [./left]
    type = DirichletBC
    variable = u
    boundary = left
    value = 0
  [../]
  [./right]
    type = DirichletBC
    variable = u
    boundary = right
    value = 1
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)
  type = Transient
  num_steps = 20
  dt = 0.1
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  output_initial = true
  exodus = true
  print_linear_residuals = true
  print_perf_log = true
[]

[Adaptivity]

  marker = errorfrac
  max_h_level = 4

  [./Indicators]
    [./error]
      type = GradientJumpIndicator
      variable = 'u v void'
    [../]
  [../]

  [./Markers]
    [./errorfrac]
      type = ErrorFractionMarker
      refine = 0.6
      coarsen = 0.1
      indicator = error
    [../]
  [../]
[]
