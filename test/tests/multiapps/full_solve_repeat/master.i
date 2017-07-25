[Mesh]
  type = GeneratedMesh
  dim = 1
[]

[Variables]
  [./u]
  [../]
[]

[Problem]
  solve = false
  kernel_coverage_check = false
[]

[Executioner]
  type = Transient
  num_steps = 5
[]

[Postprocessors]
  [./func]
    type = FunctionValuePostprocessor
    function = 't+1'
    execute_on = 'INITIAL TIMESTEP_END'
  [../]
[]

[Outputs]
[]

[MultiApps]
  [./full_solve]
    type = FullSolveMultiApp
    execute_on = 'initial timestep_end'
    positions = '0 0 0'
    input_files = sub.i
  [../]
[]

[Transfers]
  [./right_bc]
    type = MultiAppPostprocessorTransfer
    to_postprocessor = right
    from_postprocessor = func
    direction = to_multiapp
    multi_app = full_solve
  [../]
[]
