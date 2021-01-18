[StochasticTools]
[]

[Reporters]
  [const]
    type = ConstantReporter
    real_vector_names = 'const'
    real_vector_values = '2 4 6 8 10'
  []
  [stats]
    type = StatisticsReporter
    reporters = 'const/const'
    compute = 'min max sum mean stddev norm2 ratio stderr'
    ci_method = percentile
    ci_levels = '0.1 0.5'
  []
[]

[Outputs/out]
  type = JSON
  execute_on = FINAL
  execute_system_information_on = NONE
[]
