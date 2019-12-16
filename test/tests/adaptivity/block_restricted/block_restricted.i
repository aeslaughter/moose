[Mesh]
  [gmg]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 2
    ny = 2
  []
  [subdomains]
    type = SubdomainBoundingBoxGenerator
    input = gmg
    bottom_left = '0 0 0'
    top_right = '0.5 0.5 0'
    block_id = 1
  []
[]

[Variables/u]
[]

[Problem]
  solve = false
[]

[Adaptivity]
  [Indicators]
    [error]
      type = GradientJumpIndicator
      variable = u
      block = 1
    []
  []
  [Markers]
    [fraction]
      type = ErrorFractionMarker
      indicator = error
      block = 1
    []
  []
[]

[Executioner]
  type = Transient
  solve_type = 'PJFNK'
  num_steps = 1
[]

[Outputs]
  exodus = true
[]
