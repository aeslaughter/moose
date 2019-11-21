[Mesh]
  type = GeneratedMesh
  dim = 1
[]

[Problem]
  kernel_coverage_check = false
  solve = false
[]

[Distributions]
  [uniform_flux]
    type = UniformDistribution
    lower_bound = 100
    upper_bound = 200
  []
  [uniform_value]
    type = UniformDistribution
    lower_bound = 0
    upper_bound = 1
  []
[]

[Samplers]
  [mc]
    type = MonteCarloSampler
    num_rows = 10
    distributions = 'uniform_flux uniform_value'
  []
[]

[Executioner]
  type = Steady
[]

[MultiApps]
  [runner]
    type = SamplerFullSolveMultiApp
    sampler = mc
    input_files = 'sub.i'
  []
[]

[Transfers]
  [transfer]
    type = SamplerTransfer
    multi_app = runner
    parameters = 'BCs/left/value BCs/right/value'
    to_control = stochastic
    execute_on = INITIAL
    check_multiple_execute_on = false
  []

  [data]
    type = SamplerPostprocessorTransfer
    multi_app = runner
    vector_postprocessor = storage
    postprocessor = avg_temp_out
    execute_on = timestep_end
    check_multiapp_execute_on = false
  []
[]

[VectorPostprocessors]
  [storage]
    type = StochasticResults
    outputs = results
  []
[]

[Outputs]
  [results]
    type = CSV
    execute_on = FINAL
  []
[]
