[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 30
  xmin = 0
  xmax = 2
  ymin = 0
  ymax = 6
[]

[Variables]
  [./u]
    initial_condition = 1
  [../]
[]

#[AuxVariables]
#  [./v]
#    initial_condition = 2
#  [../]
#[]

[Kernels]
  [./diff]
    type = CoefDiffusion
    variable = u
    coef = 0.1
  [../]
  [./time]
    type = TimeDerivative
    variable = u
  [../]
[]

[BCs]
  [./bottom]
    type = DirichletBC
    variable = u
    boundary = bottom
    value = 1
  [../]
  [./top]
    type = DirichletBC
    variable = u
    boundary = top
    value = 2
  [../]
[]

[Executioner]
  # Preconditioned JFNK (default)
  type = Transient
  num_steps = 20
  dt = 0.1
  solve_type = PJFNK
  petsc_options_iname = '-pc_type -pc_hypre_type'
  petsc_options_value = 'hypre boomeramg'
[]

[Postprocessors]
  [./average]
    type = ElementAverageValue
    variable = u
  [../]

[MultiApps]
  #active = ''
  [./sub]
    type = TransientMultiApp
    app_type = MooseTestApp
    positions = '0. 0. 0.'
    input_files = sub.i
    execute_on = 'initial timestep_end'
    output_in_position = true
  [../]
[]

[Transfers]
  active = ''#ub_bc'
  [./sub_bc]
    type = MultiAppPostprocessorTransfer
    multi_app = sub
    direction = to_multiapp
    from_postprocessor = average
    to_postprocessor = reciever
  [../]
  [./sub_u]
    type = MultiAppCopyTransfer
    direction = from_multiapp
    multi_app = sub
    variable = v
    source_variable = u
  [../]
[]

[Outputs]
  exodus = true
[]
