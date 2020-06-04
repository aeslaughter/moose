[StochasticTools]
[]

[Distributions]
  [standard_normal]
    type = Normal
    mean = 0
    standard_deviation = 1
  []
[]

[VectorPostprocessors]
  [old_faithful]
     type = CSVReader
     csv_file = "../../data/old_faithful.csv"
     execute_on = INITIAL
  []
[]


[UserObjects] #[ObjectiveFunctions]
  [cost]
    type = PolynomialLeastSquares
    vector_postprocessor = old_faithful
    x_vector = "duration"
    y_vector = "wait"
    #execute_on = TIMESTEP_BEGIN
  []
[]


[Trainers]
  [GD]
    type = GradientDescentTrainer
    objective_function = cost
    max_iterations = 10000
    step_size = 0.00001
  []
[]
