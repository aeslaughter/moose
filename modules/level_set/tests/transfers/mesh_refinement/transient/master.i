[Mesh]
  type = GeneratedMesh
  dim = 2
  xmax = 10
  ymax = 10
  nx = 10
  ny = 10
  uniform_refine = 2
[]


[Adaptivity]
  initial_marker = marker
  marker = marker
  initial_steps = 1
  max_h_level = 1
  [./Indicators]
    [./jump]
      type = GradientJumpIndicator
      variable = u
    [../]
  [../]
  [./Markers]
    [./marker]
      type = ErrorFractionMarker
      refine = 0.7
      coarsen = 0.1
      indicator = jump
    [../]
  [../]
[]

[Variables]
  [./u]
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

[MultiApps]
  [./sub]
    type = FullSolveMultiApp
    input_files = 'sub.i'
    execute_on = 'timestep_end'
  [../]
[]

[Transfers]
  [./refine]
    type = LevelSetMeshRefinementTransfer
    direction = to_multiapp
    multi_app = sub
    marker = marker
  [../]
[]

[Executioner]
  type = Transient
  num_steps = 20
  dt = 1
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  exodus = true
[]
