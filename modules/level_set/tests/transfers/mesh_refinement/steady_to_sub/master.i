[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 8
  ny = 8
[]

[Adaptivity]
  marker = marker
  #initial_steps = 1
  [./Markers]
    [./marker]
      type = BoxMarker
      bottom_left = '0.25, 0.25, 0.0'
      top_right = '0.75 0.75 0.0'
      inside = REFINE
      outside = DO_NOTHING
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

[UserObjects]
  [./mesh_refine]
    type = LevelSetMeshRefinementTracker
    execute_on = 'timestep_end'
  [../]
[]

[MultiApps]
  active = ''
  [./sub]
    type = FullSolveMultiApp
    input_files = 'sub.i'
    execute_on = 'initial timestep_end'
  [../]
[]

[Transfers]
  active = ''
  [./refine]
    type = LevelSetMeshRefinementTransfer
    direction = to_multiapp
    multi_app = sub
  [../]
[]

[Executioner]
  type = Transient
  nl_abs_tol = 1e-14
  num_steps = 2
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Outputs]
  exodus = true
[]
