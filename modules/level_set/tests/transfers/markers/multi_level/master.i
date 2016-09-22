[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Adaptivity]
  marker = marker
  max_h_level = 2
  cycles_per_step = 2
  [./Indicators]
    [./error]
      type = GradientJumpIndicator
      variable = u
    [../]
  [../]
  [./Markers]
    [./marker]
      type = ErrorFractionMarker
      coarsen = 0.1
      refine = 0.8
      indicator = error
    [./]
  [../]
[]

[Variables]
  [./u]
  [../]
[]

[Kernels]
  [./time]
    type = TimeDerivative
    variable = u
  [../]
  [./diff]
    type = Diffusion
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

[Problem]
  type = LevelSetProblem
[]

[Executioner]
  type = LevelSetExecutioner
  num_steps = 2
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[MultiApps]
  active = ''
  [./sub]
    type = LevelSetReinitializationMultiApp
    input_files = 'sub.i'
    execute_on = CUSTOM
  [../]
[]

[Transfers]
  active = ''
  [./marker_to_sub]
    type = LevelSetMeshRefinementTransfer
    multi_app = sub
    source_variable = marker
    variable = marker
  [../]
[]

[Outputs]
  exodus = true
[]
