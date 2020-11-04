[Mesh/gen]
  type = GeneratedMeshGenerator
  dim = 1
[]

[Problem]
  solve = false
[]

[Executioner]
  type = Transient
  num_steps = 4
[]

[Controls/enable]
  type = TimePeriod
  enable_objects = 'Postprocessors/value'
  start_time = 2
[]

[Postprocessors/value]
  type = TestTimePeriodTimestepSetup
[]

[Outputs]
  csv = true
[]
