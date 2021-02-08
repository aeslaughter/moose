mu=1.1
rho=1.1
advected_interp_method='average'
velocity_interp_method='rc'

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 2
    xmin = 0
    xmax = 5
    ymin = 0
    ymax = 1
    nx = 20
    ny = 10
  []
[]

[Problem]
  kernel_coverage_check = false
  fv_bcs_integrity_check = true
[]

[Variables]
  inactive = 'lambda'
  [u]
    type = PINSFVVelocityVariable
    initial_condition = 1
  []
  [v]
    type = PINSFVVelocityVariable
    initial_condition = 1e-6
  []
  [pressure]
    type = INSFVPressureVariable
  []
  [lambda]
    family = SCALAR
    order = FIRST
  []
[]

[AuxVariables]
  [porosity]
    family = MONOMIAL
    order = CONSTANT
    fv = true
    initial_condition = 1
  []
[]

[FVKernels]
  inactive = 'mean-pressure'
  [mass]
    type = PINSFVMassAdvection
    variable = pressure
    advected_interp_method = ${advected_interp_method}
    velocity_interp_method = ${velocity_interp_method}
    vel = 'velocity'
    pressure = pressure
    u = u
    v = v
    mu = ${mu}
    rho = ${rho}
  []

  [u_advection]
    type = PINSFVMomentumAdvection
    variable = u
    advected_quantity = 'rhou'
    vel = 'velocity'
    advected_interp_method = ${advected_interp_method}
    velocity_interp_method = ${velocity_interp_method}
    pressure = pressure
    u = u
    v = v
    mu = ${mu}
    rho = ${rho}
    porosity = porosity
  []
  [u_viscosity]
    type = PINSFVMomentumDiffusion
    variable = u
    mu = ${mu}
    porosity = porosity
  []
  [u_pressure]
    type = PINSFVMomentumPressure
    variable = u
    momentum_component = 'x'
    p = pressure
    porosity = porosity
  []

  [v_advection]
    type = PINSFVMomentumAdvection
    variable = v
    advected_quantity = 'rhov'
    vel = 'velocity'
    advected_interp_method = ${advected_interp_method}
    velocity_interp_method = ${velocity_interp_method}
    pressure = pressure
    u = u
    v = v
    mu = ${mu}
    rho = ${rho}
    porosity = porosity
  []
  [v_viscosity]
    type = PINSFVMomentumDiffusion
    variable = v
    mu = ${mu}
    porosity = porosity
  []
  [v_pressure]
    type = PINSFVMomentumPressure
    variable = v
    momentum_component = 'y'
    p = pressure
    porosity = porosity
  []

  [mean-pressure]
    type = FVScalarLagrangeMultiplier
    variable = pressure
    lambda = lambda
    phi0 = 0.01
  []
[]

[FVBCs]
  inactive = 'symmetry-u symmetry-v symmetry-p no-slip-u no-slip-v inlet-p outlet-p-novalue outlet-u outlet-v'
  [inlet-u]
    type = INSFVInletVelocityBC
    boundary = 'left'
    variable = u
    function = '1'
  []
  [inlet-v]
    type = INSFVInletVelocityBC
    boundary = 'left'
    variable = v
    function = 0
  []
  [inlet-p]
    type = INSFVOutletPressureBC
    boundary = 'left'
    variable = pressure
    function = 1
  []

  [free-slip-u]
    type = INSFVNaturalFreeSlipBC
    boundary = 'top bottom'
    variable = u
  []
  [free-slip-v]
    type = INSFVNaturalFreeSlipBC
    boundary = 'top bottom'
    variable = v
  []

  [no-slip-u]
    type = INSFVNoSlipWallBC
    boundary = 'top bottom'
    variable = u
    function = 0
  []
  [no-slip-v]
    type = INSFVNoSlipWallBC
    boundary = 'top bottom'
    variable = v
    function = 0
  []

  [symmetry-u]
    type = PINSFVSymmetryVelocityBC
    boundary = 'bottom'
    variable = u
    u = u
    v = v
    mu = ${mu}
    momentum_component = 'x'
    porosity = porosity
  []
  [symmetry-v]
    type = PINSFVSymmetryVelocityBC
    boundary = 'bottom'
    variable = v
    u = u
    v = v
    mu = ${mu}
    momentum_component = 'y'
    porosity = porosity
  []
  [symmetry-p]
    type = INSFVSymmetryPressureBC
    boundary = 'bottom'
    variable = pressure
  []

  [outlet-p]
    type = INSFVOutletPressureBC
    boundary = 'right'
    variable = pressure
    function = 0
  []
  [outlet-p-novalue]
    type = INSFVMassAdvectionOutflowBC
    boundary = 'right'
    variable = pressure
    u = u
    v = v
    rho = ${rho}
  []
  [outlet-u]
    type = INSFVMomentumAdvectionOutflowBC
    boundary = 'right'
    variable = u
    vel = velocity
    u = u
    v = v
  []
  [outlet-v]
    type = INSFVMomentumAdvectionOutflowBC
    boundary = 'right'
    variable = v
    vel = velocity
    u = u
    v = v
  []
[]

[Materials]
  [ins_fv]
    type = INSFVMaterial
    u = 'u'
    v = 'v'
    pressure = 'pressure'
    rho = ${rho}
  []
[]

[Executioner]
  type = Steady
  solve_type = 'NEWTON'
  # Executioner chosen for repeatability, consider asm or others for performance
  petsc_options_iname = '-pc_type -pc_factor_shift_type'
  petsc_options_value = 'lu       NONZERO'
  line_search = 'none'
  nl_rel_tol = 1e-11
  nl_abs_tol = 1e-14
[]

# Some basic Postprocessors to visually examine the solution
[Postprocessors]
  [inlet-p]
    type = SideIntegralVariablePostprocessor
    variable = pressure
    boundary = 'left'
  []
  [outlet-u]
    type = SideIntegralVariablePostprocessor
    variable = u
    boundary = 'right'
  []
[]

[Outputs]
  exodus = true
[]
