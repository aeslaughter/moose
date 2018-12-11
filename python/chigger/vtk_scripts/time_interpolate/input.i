[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
[]

[Variables]
  [./var]
    outputs = none
  [../]
[]

[AuxVariables]
  [u]
  []
[]

[AuxKernels]
  [u]
    type = FunctionAux
    function = func
    variable = u
  []
[]

[Functions]
  [func]
    type = ParsedFunction
    value = 'x*y*(t+3)'
  []
[]

[ICs]
  [u]
    type = FunctionIC
    function = func
    variable = u
  []
[]

[Problem]
  type = FEProblem
  solve = false
  kernel_coverage_check = false
[]


[Executioner]
  type = Transient
  start_time = -7
  num_steps = 2
  dt = 9
[]

[Adaptivity]
  marker = box
  cycles_per_step = 2
  [Markers]
    [box]
      type = BoxMarker
      bottom_left = '0.2 0.2 0'
      top_right = '0.5 0.7 0'
      inside = refine
      outside = do_nothing
    []
  []
[]

[Outputs]
  [out]
    type = Exodus
    execute_on = TIMESTEP_END
  []
[]
