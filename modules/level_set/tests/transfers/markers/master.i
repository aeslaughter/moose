[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Adaptivity]
  marker = marker
  max_h_level = 1
  [./Markers]
    [./marker]
      type = BoxMarker
      bottom_left = '0.25 0.25 0'
      top_right = '0.75 0.75 0'
      outside =  DO_NOTHING
      inside = REFINE
    [../]
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
  type = Transient
  num_steps = 2
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[MultiApps]
  [./sub]
    type = LevelSetReinitializationMultiApp
    input_files = 'sub.i'
    execute_on = timestep_end
  [../]
[]

[Transfers]
  [./marker_to_sub]
    type = MultiAppCopyTransfer
    multi_app = sub
    direction = to_multiapp
    from_variable = marker
    to_variable = marker
    execute_on = CUSTOM
  [../]
[]

[Outputs]
  exodus = true
[]
