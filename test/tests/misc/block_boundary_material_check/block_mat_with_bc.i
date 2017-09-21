[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 2
  ny = 2
[]

[Debug]
  show_material_props = true
[]

[MeshModifiers]
  [./subdomain1]
    type = SubdomainBoundingBox
    bottom_left = '0 0 0'
    top_right = '0.5 0.5 0'
    block_id = 1
  [../]
[]

[Variables]
  [./u]
  [../]
[]

[BCs]
  [./vacuum]
    type = DGMDDBC
    variable = u
    boundary = 'left right top bottom'
    epsilon = 1
    sigma = 4
    prop_name = prop
    function = '0'
  [../]
[]

[Materials]
  [./missing]
    type = GenericConstantMaterial
    block = '1'
    prop_names = 'prop'
    prop_values = '42'
  [../]
  [./other]
    type = GenericConstantMaterial
    block = '0 1'
    prop_names = 'other'
    prop_values = '43'
  [../]
[]

[Problem]
  type = FEProblem
  solve = false
  kernel_coverage_check = false
[]

[Executioner]
  type = Steady
[]

[Outputs]
[]
