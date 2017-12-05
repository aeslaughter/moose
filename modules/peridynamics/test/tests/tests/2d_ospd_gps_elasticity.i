[GlobalParams]
  displacements = 'disp_x disp_y'
  scalar_out_of_plane_strain = scalar_strain_zz
  bond_status = bond_status
  full_jacobian = true
[]

[Mesh]
  type = GeneratedMeshPD
  dim = 2
  nx = 100
  horizon_number = 3
[]

[Variables]
  [./disp_x]
  [../]
  [./disp_y]
  [../]
  [./scalar_strain_zz]
    order = FIRST
    family = SCALAR
  [../]
[]

[AuxVariables]
  [./temp]
    order = FIRST
    family = LAGRANGE
  [../]

  [./stress_zz]
    order = FIRST
    family = LAGRANGE
  [../]
[]

[Modules]
  [./Peridynamics]
    [./Master]
      formulation = OrdinaryState
    [../]
    [./GeneralizedPlaneStrain]
      [./gps]
        formulation = OrdinaryState
        out_of_plane_stress_variable = stress_zz
      [../]
    [../]
  [../]
[]

[AuxKernels]
  [./tempfuncaux]
    type = FunctionAux
    variable = temp
    function = tempfunc
    use_displaced_mesh = false
  [../]
  [./stress_zz]
    type = NodalStressStrainAux
    rank_two_tensor = stress
    variable = stress_zz

    poissons_ratio = 0.3
    youngs_modulus = 1e6
    thermal_expansion_coeff = 1.0e-5
    stress_free_temperature = 0.5

    quantity_type = Component
    index_i = 2
    index_j = 2
  [../]
[]

[Functions]
  [./tempfunc]
    type = ParsedFunction
    value = '(1-x)*100*t'
  [../]
[]

[BCs]
  [./bottomx]
    type = PresetBC
    boundary = 2
    variable = disp_x
    value = 0.0
  [../]
  [./bottomy]
    type = PresetBC
    boundary = 2
    variable = disp_y
    value = 0.0
  [../]
[]

[Materials]
  [./elastic_tensor]
    type = OSPDSmallStrainConstantHorizon
    poissons_ratio = 0.3
    youngs_modulus = 1e6
    temperature = temp
    thermal_expansion_coeff = 1.0e-5
    stress_free_temperature = 0.5
  [../]
[]

[Preconditioning]
  [./SMP]
    type = SMP
    full = true
  [../]
[]

[Executioner]
  type = Transient

  solve_type = PJFNK
  line_search = none

  # nl_rel_tol = 1e-12

  start_time = 0.0
  end_time = 1.0
[]

[Outputs]
  exodus = true
[]
