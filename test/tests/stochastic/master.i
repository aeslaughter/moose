[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]

[Variables]
  [./u]
  [../]
[]

[Problem]
  type = FEProblem
  solve = false
[../]

[Executioner]
  type = Transient
  num_steps = 1
  dt = 1
[]

# [Samplers]
[VectorPostprocessors]
  [./k_sample]
    type = NormalDistribution
    mean = 3
    standard_deviation = 0.75
    count = 5
    execute_on = 'initial'
  [../]
  [./receive]
    type = VectorReceiver
    default = 42
    count = 5
  [../]
[]

[Outputs]
  csv = true
[]

[MultiApps]
  [./full_solve]
    type = FullSolveMultiApp
    execute_on = 'timestep_begin'
    positions = '0 0 0
                 0 0 0
                 0 0 0
                 0 0 0
                 0 0 0'
    input_files = 'sub.i'
  [../]
[]

[Transfers]
  [./to_sub]
    type = MultiAppVectorPostprocessorTransfer
    vector_postprocessor = 'k_sample'
    vector_postprocessor_vector_name = 'distribution'
    postprocessor = conductivity
    direction = TO_MULTIAPP
    multi_app = full_solve
  [../]
  [./from_sub]
    type = MultiAppVectorPostprocessorTransfer
    vector_postprocessor = 'receive'
    vector_postprocessor_vector_name = 'vector'
    postprocessor = side_average
    direction = FROM_MULTIAPP
    multi_app = full_solve
  [../]

[]
